using System.Numerics;
using System.Text.Json;
using ImGuiNET;
using RecompOne.Runtime.Hardware;

namespace NascarRumble.Host;

/// <summary>
/// Start screen shown after the disc is validated and before the game boots, styled after the
/// game's own menus (see docs/LAUNCHER.md). It sets the race frame rate and the debug mode.
/// The background is the game's title art, decoded from the user's disc (CW/FEND/FELD.LSC).
/// </summary>
public static class Launcher
{
    private const string PrefsFile = "launcher.json";

    public sealed class Prefs
    {
        public int Fps { get; set; } = 30;
        public bool Debug { get; set; }
    }

    private enum Item { Start, FrameRate, Debug, Quit }

    private static readonly Item[] Items = [Item.Start, Item.FrameRate, Item.Debug, Item.Quit];

    private static Prefs _prefs = new();
    private static int _selected;
    private static ushort _previousButtons = 0xFFFF;
    private static bool _done;
    private static nint _background;
    private static int _backgroundWidth, _backgroundHeight;
    private static ImFontPtr? _itemFont, _hintFont;

    /// <summary>Fonts must be requested before the window creates its ImGui context.</summary>
    public static void RequestFonts()
    {
        const string fonts = "/System/Library/Fonts/Supplemental/";
        RecompOne.Runtime.Runtime.UiFontRequests.Add((fonts + "Arial Narrow Bold.ttf", 40f));
        RecompOne.Runtime.Runtime.UiFontRequests.Add((fonts + "Arial Narrow Bold.ttf", 26f));
    }

    /// <summary>Loads saved choices and applies them without showing the screen.</summary>
    public static Prefs LoadAndApply()
    {
        _prefs = Load();
        Apply(_prefs);
        return _prefs;
    }

    /// <summary>Runtime.PreBoot callback: shows the screen until Start Game is chosen.</summary>
    public static void Run()
    {
        _prefs = Load();
        if (RecompOne.Runtime.Runtime.UiFonts is [var item, var hint, ..])
        {
            _itemFont = item;
            _hintFont = hint;
        }
        LoadBackground();
        RecompOne.Runtime.Runtime.TopBarOverride = false;
        var previousOverlay = RecompOne.Runtime.Runtime.UiOverlay;
        RecompOne.Runtime.Runtime.UiOverlay = Draw;
        _previousButtons = Controller.State;
        while (!_done)
        {
            RecompOne.Runtime.Runtime.PumpUi();
            HandleInput();
            Thread.Sleep(10);
        }
        RecompOne.Runtime.Runtime.UiOverlay = previousOverlay;
        Save(_prefs);
        Apply(_prefs);
    }

    private static void Apply(Prefs prefs)
    {
        NativeHooks.SetRaceFrameRate(prefs.Fps);
        RecompOne.Runtime.Runtime.TopBarOverride = prefs.Debug;
        NativeHooks.LapLogEnabled |= prefs.Debug;
        if (prefs.Debug) RecompOne.Runtime.Runtime.UiOverlay = DebugHud.Draw;
        Console.Error.WriteLine($"[launcher] race fps={prefs.Fps} debug={(prefs.Debug ? "on" : "off")}");
    }

    private static void HandleInput()
    {
        ushort now = Controller.State;
        bool Pressed(ushort bit) => (now & bit) == 0 && (_previousButtons & bit) != 0;
        if (Pressed(Controller.Up)) _selected = (_selected + Items.Length - 1) % Items.Length;
        if (Pressed(Controller.Down)) _selected = (_selected + 1) % Items.Length;
        bool change = Pressed(Controller.Left) || Pressed(Controller.Right);
        bool confirm = Pressed(Controller.Cross) || Pressed(Controller.Start);
        switch (Items[_selected])
        {
            case Item.FrameRate when change || confirm:
                _prefs.Fps = _prefs.Fps == 60 ? 30 : 60;
                break;
            case Item.Debug when change || confirm:
                _prefs.Debug = !_prefs.Debug;
                break;
            case Item.Start when confirm:
                _done = true;
                break;
            case Item.Quit when confirm:
                Save(_prefs);
                RecompOne.Runtime.Runtime.Shutdown();
                Environment.Exit(0);
                break;
        }
        _previousButtons = now;
    }

    private static void LoadBackground()
    {
        try
        {
            using var disc = RecompOne.Runtime.Cdrom.CueFs.Open(RecompOne.Runtime.Runtime.CdPath);
            var (rgba, width, height) = LscImage.Decode(disc.ReadFile("CW/FEND/FELD.LSC"));
            _background = RecompOne.Runtime.Runtime.CreateUiTexture(rgba, width, height);
            (_backgroundWidth, _backgroundHeight) = (width, height);
        }
        catch (Exception error)
        {
            Console.Error.WriteLine($"[launcher] title art unavailable: {error.Message}");
        }
    }

    // Palette sampled from the game's main menu.
    private static readonly uint Yellow = Rgba(248, 232, 48);
    private static readonly uint White = Rgba(240, 240, 240);
    private static readonly uint Lavender = Rgba(196, 188, 236);
    private static readonly uint BoxFill = Rgba(8, 8, 16, 190);
    private static readonly uint SelectedFill = Rgba(112, 12, 16, 235);
    private static readonly uint ValueFill = Rgba(36, 36, 40, 220);
    private static readonly uint Shadow = Rgba(0, 0, 0, 200);

    private static uint Rgba(int r, int g, int b, int a = 255) =>
        (uint)(r | (g << 8) | (b << 16) | (a << 24));

    private static void Draw()
    {
        var io = ImGui.GetIO();
        var display = io.DisplaySize;
        var dl = ImGui.GetForegroundDrawList();
        dl.AddRectFilled(Vector2.Zero, display, Rgba(0, 0, 0));

        // 4:3 screen, letterboxed, like the game's output.
        float height = MathF.Min(display.Y, display.X * 3f / 4f);
        float width = height * 4f / 3f;
        var origin = new Vector2((display.X - width) / 2f, (display.Y - height) / 2f);
        float unit = height / 240f;
        Vector2 P(float x, float y) => origin + new Vector2(x, y) * unit;

        if (_background != 0)
        {
            // The title art is 320x256; crop to the 240 visible lines, keeping the logo.
            float v1 = 240f / _backgroundHeight;
            dl.AddImage(_background, origin, origin + new Vector2(width, height), Vector2.Zero, new Vector2(1, v1));
        }
        dl.AddRectFilledMultiColor(P(0, 120), P(320, 240), Rgba(0, 0, 0, 0), Rgba(0, 0, 0, 0),
            Rgba(0, 0, 0, 170), Rgba(0, 0, 0, 170));

        var itemFont = _itemFont ?? ImGui.GetFont();
        var hintFont = _hintFont ?? ImGui.GetFont();
        float itemSize = 15f * unit, hintSize = 9.5f * unit;

        // Hint box, top right, like "Select this for 1 player mode."
        string hint = Items[_selected] switch
        {
            Item.Start => "Start the game with these settings.",
            Item.FrameRate => _prefs.Fps == 60
                ? "60 fps races. Experimental: launch grip differs slightly."
                : "30 fps races, the console's own cadence.",
            Item.Debug => _prefs.Debug
                ? "Shows the Debug menu bar, race HUD and lap log."
                : "Clean screen, no debug tools.",
            _ => "Close the game.",
        };
        DrawHintBox(dl, hintFont, hintSize, hint, P(214, 86), P(312, 122));

        // Menu box.
        var boxMin = P(84, 128);
        var boxMax = P(236, 128 + Items.Length * 19f + 8f);
        dl.AddRectFilled(boxMin, boxMax, BoxFill, 6f * unit);
        dl.AddRect(boxMin, boxMax, Lavender, 6f * unit, ImDrawFlags.None, 1.6f * unit);

        for (int i = 0; i < Items.Length; i++)
        {
            var rowMin = P(88, 132 + i * 19f);
            var rowMax = P(232, 132 + i * 19f + 18f);
            bool selected = i == _selected;
            if (selected) dl.AddRectFilled(rowMin, rowMax, SelectedFill, 2f * unit);
            string label = Items[i] switch
            {
                Item.Start => "Start Game",
                Item.FrameRate => "Frame Rate",
                Item.Debug => "Debug Mode",
                _ => "Quit",
            };
            var textPos = rowMin + new Vector2(5f * unit, 1.5f * unit);
            dl.AddText(itemFont, itemSize, textPos + new Vector2(1, 1) * unit, Shadow, label);
            dl.AddText(itemFont, itemSize, textPos, selected ? Yellow : White, label);

            string? value = Items[i] switch
            {
                Item.FrameRate => _prefs.Fps == 60 ? "60 FPS" : "30 FPS",
                Item.Debug => _prefs.Debug ? "On" : "Off",
                _ => null,
            };
            if (value == null) continue;
            DrawArrows(dl, P(200, 132 + i * 19f + 9f), unit, selected);
            var valueMin = P(244, 132 + i * 19f + 1f);
            var valueMax = P(304, 132 + i * 19f + 17f);
            dl.AddRectFilled(valueMin, valueMax, ValueFill, 1.5f * unit);
            dl.AddRect(valueMin, valueMax, Rgba(150, 150, 160), 1.5f * unit, ImDrawFlags.None, 1.2f * unit);
            dl.AddText(itemFont, itemSize * 0.9f, valueMin + new Vector2(5f * unit, 0.5f * unit), selected ? Yellow : White, value);
        }

        // Footer legend.
        string legend = "X Advance    Up/Down Change Selection    Left/Right Change Setting";
        var legendSize = hintFont.CalcTextSizeA(hintSize, float.MaxValue, 0f, legend);
        var legendPos = P(160, 224) - new Vector2(legendSize.X / 2f, 0);
        dl.AddText(hintFont, hintSize, legendPos + new Vector2(1, 1) * unit, Shadow, legend);
        dl.AddText(hintFont, hintSize, legendPos, Yellow, legend);

        dl.AddText(hintFont, hintSize * 0.8f, P(6, 4), Rgba(200, 200, 210, 200), "NASCAR Rumble Native - fan project");
    }

    private static void DrawArrows(ImDrawListPtr dl, Vector2 center, float unit, bool selected)
    {
        uint color = selected ? Yellow : White;
        float s = 3.5f * unit;
        var l = center + new Vector2(-6f * unit, 0);
        var r = center + new Vector2(6f * unit, 0);
        dl.AddTriangleFilled(l + new Vector2(-s, 0), l + new Vector2(s * 0.6f, -s), l + new Vector2(s * 0.6f, s), color);
        dl.AddTriangleFilled(r + new Vector2(s, 0), r + new Vector2(-s * 0.6f, -s), r + new Vector2(-s * 0.6f, s), color);
    }

    private static void DrawHintBox(ImDrawListPtr dl, ImFontPtr font, float size, string text, Vector2 min, Vector2 max)
    {
        float unit = (max.Y - min.Y) / 36f;
        dl.AddRectFilled(min, max, Rgba(24, 24, 28, 220), 4f * unit);
        dl.AddRect(min, max, Lavender, 4f * unit, ImDrawFlags.None, 1.4f * unit);
        float wrap = max.X - min.X - 8f * unit;
        var textSize = font.CalcTextSizeA(size, float.MaxValue, wrap, text);
        var pos = new Vector2((min.X + max.X - textSize.X) / 2f, (min.Y + max.Y - textSize.Y) / 2f);
        dl.AddText(font, size, pos, Yellow, text, wrap);
    }

    private static Prefs Load()
    {
        try
        {
            if (File.Exists(PrefsFile))
                return JsonSerializer.Deserialize<Prefs>(File.ReadAllText(PrefsFile)) ?? new Prefs();
        }
        catch (Exception error)
        {
            Console.Error.WriteLine($"[launcher] ignoring {PrefsFile}: {error.Message}");
        }
        return new Prefs();
    }

    private static void Save(Prefs prefs)
    {
        try
        {
            File.WriteAllText(PrefsFile, JsonSerializer.Serialize(prefs, new JsonSerializerOptions { WriteIndented = true }));
        }
        catch (Exception error)
        {
            Console.Error.WriteLine($"[launcher] could not save {PrefsFile}: {error.Message}");
        }
    }
}
