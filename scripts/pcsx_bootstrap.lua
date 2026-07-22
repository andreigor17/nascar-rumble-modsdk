PCSX.WebServer = PCSX.WebServer or {}
PCSX.WebServer.Handlers = PCSX.WebServer.Handlers or {}
local function urldecode(s)
  s = s:gsub('+',' '):gsub('%%(%x%x)', function(h) return string.char(tonumber(h,16)) end)
  return s
end
PCSX.WebServer.Handlers['x'] = function(req)
  local c
  local q = req.urlData and req.urlData.query
  if q then local m = q:match('code=(.*)'); if m then c = urldecode(m) end end
  if not c and req.form and req.form.code and req.form.code[1] then c = req.form.code[1] end
  if not c then return 'DIAG method='..tostring(req.method)..' query='..tostring(q) end
  local f,e = load(c); if not f then return 'ERR '..tostring(e) end
  local ok,r = pcall(f); if not ok then return 'RUNERR '..tostring(r) end
  return tostring(r)
end
print('[bootstrap] canal /api/v1/lua/x pronto (query code=)')
