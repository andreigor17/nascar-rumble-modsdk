/*
 * champ_any_car — hook do grid de oponentes do NASCAR Rumble (PS1, SLUS_010.68)
 *
 * Permite escolher QUALQUER carro (qualquer piloto, qualquer classe) como oponente
 * no Championship, onde o jogo normalmente monta o grid sozinho via RNG.
 *
 * Alvo (ver docs/FUNCTION_MAP.md, seção "Grid de oponentes"):
 *   grid_build  0x8008927c  monta o grid (conta + identidades), seleciona oponentes via RNG
 *   grid_spawn  0x8003132c  lê a tabela e instancia os carros na largada
 *   tabela      0x800b0e40  [+0]=nº de carros; N entradas de 8 bytes
 *
 * Estratégia: WRAPPER pós-grid_build. Deixamos o jogo montar o grid inteiro
 * (contagem, posições, embaralhamento, pools) e só REESCREVEMOS o byte +2
 * (model ID) das entradas de IA. Roda antes do carregamento de recursos, então
 * o loader traz as liveries (Cpag) / modelos (Cobj) certos.
 */

typedef unsigned char  u8;
typedef unsigned int   u32;

/* ---------------- tabela do grid (layout medido ao vivo) ---------------- */

#define GRID_BASE     ((volatile u8 *)0x800B0E40)
#define GRID_COUNT    (GRID_BASE[0])          /* nº de carros na corrida */
#define ENT(i)        (GRID_BASE + (i) * 8)

#define ENT_FLAG(i)   (ENT(i)[0])             /* 0x01 no jogador, 0x00 nos oponentes */
#define ENT_TYPE(i)   (ENT(i)[1])             /* 0xFF = IA, 0x00 = jogador  <== seletor */
#define ENT_MODEL(i)  (ENT(i)[2])             /* MODEL ID  <== o que injetamos */
#define ENT_POS(i)    (ENT(i)[4])             /* ordem de largada */

/* ---------------- model ID = piloto + 56 * classe ---------------- */

#define ROOKIE(p)  ((u8)(p))            /* p = 0..55 */
#define PRO(p)     ((u8)((p) + 56))
#define ELITE(p)   ((u8)((p) + 112))

/* índices de piloto úteis (de docs/cars_wiki.csv; p = id da faixa Rookie) */
#define P_RUSTY_WALLACE   1
#define P_JEFF_GORDON     14
#define P_RON_HORNADAY    35
#define P_KENNY_WALLACE   26
#define P_BILL_ELLIOTT    30
#define P_JEFF_BURTON     32

/* ---------------- LISTA DE OPONENTES (edite aqui) ----------------
 * Aplicada em ordem às entradas de IA do grid. Se a lista for menor que o
 * número de oponentes, os restantes ficam como o jogo sorteou.
 */
static const u8 kOpponents[] = {
    ELITE(P_RUSTY_WALLACE),
    ELITE(P_BILL_ELLIOTT),
    ELITE(P_JEFF_BURTON),
    PRO(P_KENNY_WALLACE),
    PRO(P_RON_HORNADAY),
};
#define K_NUM_OPPONENTS (sizeof(kOpponents) / sizeof(kOpponents[0]))

/* ---------------- função original ---------------- */

typedef void (*grid_build_fn)(char);
#define grid_build_orig ((grid_build_fn)0x8008927C)

/* ---------------- o hook ----------------
 * Substitui os 4 `jal grid_build` do EXE. Encaminha o argumento original,
 * deixa o jogo montar tudo, e só então sobrescreve as identidades de IA.
 */
void grid_build_hook(char mode)
{
    u8 n, i, k;

    grid_build_orig(mode);          /* 1) o jogo monta o grid normalmente */

    n = GRID_COUNT;
    if (n == 0 || n > 8) {          /* sanidade: grid do jogo é <= 8 */
        return;
    }

    k = 0;
    for (i = 0; i < n; i++) {       /* 2) reescreve só os oponentes */
        if (ENT_TYPE(i) == 0x00) {  /*    0x00 = jogador -> nunca tocar */
            continue;
        }
        if (k >= K_NUM_OPPONENTS) {
            break;                  /*    lista acabou: resto fica sorteado */
        }
        ENT_MODEL(i) = kOpponents[k];
        k++;
    }
}
