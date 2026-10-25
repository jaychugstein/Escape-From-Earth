// ESCAPE FROM EARTH - by jaychugstein. Arduboy FX / POOM.
// Fly Glorb's saucer left to right through one long course and into the mothership. Touch anything and it's over.
// Left/Right (or POOM tilt): turn the saucer   Outer button: booster (tap to hover)   Inner button: spin a quarter turn
#include <Arduboy2.h>
#include <ArduboyTones.h>
#include <EEPROM.h>
#include "font.h"
#include "fxdata.h"
#include "music.h"
Arduboy2Base ab;
ARDUBOY_NO_USB
ArduboyTones snd(ab.audio.enabled);

// ------------------------------------------------------------------ fast drawing helpers
void frect(int16_t x, int16_t y, int16_t w, int16_t h, uint8_t col) {
  if (x < 0) { w += x; x = 0; } if (y < 0) { h += y; y = 0; }
  if (x + w > 128) w = 128 - x; if (y + h > 64) h = 64 - y;
  if (w <= 0 || h <= 0) return;
  for (int16_t yy = y; yy < y + h;) {
    uint8_t pg = yy >> 3, o = yy & 7, n = min(8 - o, y + h - yy);
    uint8_t m = ((1 << n) - 1) << o;
    uint8_t* q = ab.sBuffer + pg * 128 + x;
    if (col) for (int16_t i = 0; i < w; i++) q[i] |= m; else for (int16_t i = 0; i < w; i++) q[i] &= ~m;
    yy += n;
  }
}
int16_t tx_, ty_; bool inkB;        // inkB: draw letters in black (on a white bar)
void at(int16_t x, int16_t y) { tx_ = x; ty_ = y; }
void glyph(uint8_t g) {
  for (uint8_t i = 0; i < 6; i++, tx_++) {
    if (tx_ < 0 || tx_ > 127) continue;
    uint8_t b = i < 5 ? pgm_read_byte(FONT + g * 5 + i) : 0;
    if (!b || ty_ < 0) continue;
    int16_t p = ty_ >> 3; uint8_t o = ty_ & 7;
    uint8_t* q = ab.sBuffer + p * 128 + tx_;
    uint8_t lo = b << o, hi = o ? b >> (8 - o) : 0;
    if (inkB) { if (p < 8) *q &= ~lo; if (hi && p < 7) q[128] &= ~hi; }
    else { if (p < 8) *q |= lo; if (hi && p < 7) q[128] |= hi; }
  }
}
void pc(char c) { glyph(c >= 32 && c <= 90 ? c - 32 : 0); }
void pp(PGM_P s) { char c; while ((c = pgm_read_byte(s++))) pc(c); }
void pn(int32_t v) { char b[11]; uint8_t n = 0; do { b[n++] = '0' + v % 10; v /= 10; } while (v); while (n) pc(b[--n]); }
#define PS(s) pp(PSTR(s))
// tiny 3x5 font: 0-9, A-Z, then x : ! space - + ? '
const uint8_t TINY[] PROGMEM = {31,17,31, 0,31,0, 29,21,23, 21,21,31, 7,4,31, 23,21,29, 31,21,29, 1,1,31, 31,21,31, 23,21,31,
  30,5,30, 31,21,10, 14,17,17, 31,17,14, 31,21,17, 31,5,1, 14,17,29, 31,4,31, 17,31,17, 8,16,15, 31,4,27, 31,16,16, 31,2,31,
  31,1,30, 14,17,14, 31,5,2, 14,17,30, 31,5,26, 18,21,9, 1,31,1, 15,16,15, 7,24,7, 31,8,31, 27,4,27, 3,28,3, 25,21,19,
  10,4,10, 0,10,0, 0,23,0, 0,0,0, 4,4,4, 4,14,4, 1,21,2, 0,3,0, 16,8,0, 0,16,0, 25,4,19, 3,0,3};
void tinyCol(int16_t xx, int16_t y, uint8_t b) {
  if (xx < 0 || xx > 127 || y < 0 || y > 58) return;
  uint8_t* q = ab.sBuffer + (y >> 3) * 128 + xx; uint8_t o = y & 7;
  *q |= b << o; if (o > 3 && (y >> 3) < 7) q[128] |= b >> (8 - o);
}
void tinyG(int16_t x, int16_t y, uint8_t g) { for (uint8_t i = 0; i < 3; i++) tinyCol(x + i, y, pgm_read_byte(TINY + g * 3 + i)); }
uint8_t tinyIdx(char c) {
  return c >= '0' && c <= '9' ? c - '0' : c >= 'A' && c <= 'Z' ? c - 'A' + 10 :
    c == 'x' ? 36 : c == ':' ? 37 : c == '!' ? 38 : c == '-' ? 40 : c == '+' ? 41 : c == '?' ? 42 : c == '\'' ? 43 : c == ',' ? 44 : c == '.' ? 45 : c == '%' ? 46 : c == '"' ? 47 : 39;
}
int16_t tinyS(int16_t x, int16_t y, PGM_P s) {
  char c;
  while ((c = pgm_read_byte(s++))) {
    tinyG(x, y, tinyIdx(c)); x += 4;
  }
  return x;
}
void tinyOutlined(int16_t x, int16_t y, PGM_P s) {        // tiny text with a thin black outline hugging each letter
  uint8_t n = strlen_P(s); int16_t w = n * 4;
  for (int16_t i = -1; i <= w; i++) {
    uint8_t h = 0;
    for (int8_t d = -1; d <= 1; d++) {
      int16_t c = i + d; if (c < 0 || c >= w || (c & 3) == 3) continue;
      uint8_t b = pgm_read_byte(TINY + tinyIdx(pgm_read_byte(s + (c >> 2))) * 3 + (c & 3));
      h |= (b << 1) | (b << 2) | b;                                         // rows y-1 .. y+5
    }
    for (uint8_t r = 0; r < 7; r++) if (h & (1 << r)) ab.drawPixel(x + i, y - 1 + r, BLACK);
  }
  tinyS(x, y, s);
}
int16_t tinyN(int16_t x, int16_t y, uint32_t v) {
  char b[8]; uint8_t n = 0; do { b[n++] = v % 10; v /= 10; } while (v);
  while (n) { tinyG(x, y, b[--n]); x += 4; } return x;
}
void showScreen(uint24_t a) { FX::readDataBytes(a, ab.sBuffer, 1024); }   // full-screen pictures live in FX flash

// ------------------------------------------------------------------ world
const int16_t GROUND = 57;                                             // ground line on screen
// ------------------------------------------------------------------ state
uint8_t stars[44][2];
enum { S_TITLE, S_GLORB, S_CTRL, S_MENU, S_PLAY };
uint8_t st = S_TITLE, shakeT;
uint16_t stT;
uint32_t playT;
float camx;
int16_t SX(float wx) { return (int16_t)wx - (int16_t)camx; }   // whole pixels, the same way the course is drawn, so what you see is exactly what you hit

// ------------------------------------------------------------------ the course (Pocket Rocket controls)
// Left/Right turn the saucer, hold the outer button to fire the booster (tap it to hover).
// Fly left to right through the whole course. Touch anything and it's over. Get close to the mothership and it pulls you in.
const float GRAV = 0.014f, THRUST = 0.031f, TURN = 6.2832f / 320;     // Pocket Rocket feel, a touch punchier
const float DRAG_X = 0.988f, DRAG_Y = 0.993f, TURN_SPEED = 1.3f;   // air drag keeps it from sliding around
const int16_t START_X = 66, PAD_Y = 54;                                // launch pad centre, pad top
const int16_t MS_L = 7678;                                             // left edge of the mothership picture
const int8_t BAY_L = 42, BAY_R = 80, BAY_T = 15, BAY_B = 33, MOUTH = 37;   // its open hangar bay (inside the picture); MOUTH = front edge
enum { F_READY, F_FLY, F_CRASH, F_WIN };
uint8_t fst, endT;
float rx, ry, vx, vy, legs, raF; int16_t ra;                                    // ra: 320 steps per full turn
bool thr, lock;                                                            // lock: wait for the button to be let go first
uint16_t best, dist, flyT;                                                // best distance (tenths of a metre), time in frames
float msRise; bool newBest;
// stunts and scoring
bool spinning; float spinTo, spinAcc, coastAcc;                            // coastAcc: turning done without the booster                                      // inner button: snap a quarter turn anticlockwise
uint8_t flips, popT, big720, big1080, pop720; bool got720; uint16_t upT, fuelT;                                   // full turns, frames upside down, frames boosting
uint32_t score, bestScore;
struct Wave { float x, y, ex, ey; uint8_t t; } wave[8];                    // booster waves: ))) growing as they go
struct Spark { int16_t x; int8_t y, vx, vy; uint8_t t; } spark[16];        // crash bits
struct Deb { float x, y, vx, vy, a, va; uint8_t k; } deb[6];               // saucer pieces after a crash: dome, two halves, chunks

void loadBest() { uint32_t m; EEPROM.get(96, m); if (m == 0x5A0C0DE8UL) { EEPROM.get(100, best); EEPROM.get(104, bestScore); } else { best = 0; bestScore = 0; } }
void saveBest() { EEPROM.put(96, (uint32_t)0x5A0C0DE8UL); EEPROM.put(100, best); EEPROM.put(104, bestScore); }
uint32_t stunts() { return dist + (uint32_t)flips * 500 + (uint32_t)big720 * 2000 + (uint32_t)big1080 * 5000 + (uint32_t)upT * 2; }   // dist is in tenths of a metre = 10 points a metre   // 500 a full turn, 2000 a booster-free 720, 120 a second upside down
bool solid(int16_t x, int16_t y) {                                         // is this spot part of the scenery?
  if (y < 0) return false; if (y > 63 || x < 0 || x >= LVL_W) return true;
  uint8_t b; FX::readDataBytes(FX_LVL + ((uint24_t)(y >> 3) * LVL_W + x) * 2 + 1, &b, 1);
  return b & (1 << (y & 7));
}
void burst(int16_t x, int8_t y) {
  for (uint8_t k = 0; k < 16; k++) { float a = k * 0.39f; spark[k] = {x, y, (int8_t)(cos(a) * 14), (int8_t)(sin(a) * 14 - 8), (uint8_t)(24 + random(16))}; }
}
struct Air { float x, y; uint8_t kind, t; bool on; } air[7];        // air traffic (see below)
uint8_t airT;
struct Fw { int16_t x; int8_t top; uint8_t t; } fw[3];                      // fireworks: t counts up, rising then bursting
void newGame() {
  playT = 0; shakeT = 0; endT = 0;
  for (auto& w : wave) w.t = 0;
  for (auto& s : spark) s.t = 0;
  for (auto& d : deb) d.k = 255;
  fst = F_READY; rx = START_X; ry = PAD_Y - 1 - 7; vx = vy = 0; ra = 0; legs = 4; thr = false; lock = true; dist = 0; raF = 0; flyT = 0; msRise = 0; newBest = false;
  spinning = false; spinAcc = 0; coastAcc = 0; big720 = 0; big1080 = 0; pop720 = 0; got720 = false; flips = 0; popT = 0; upT = 0; fuelT = 0; score = 0;
  for (auto& a : air) a.on = false; airT = 90;
  for (auto& f : fw) f.t = 0;
  camx = 0;
  st = S_PLAY; stT = 0; snd.noTone();
}

void setup() {
  ab.boot(); ab.display(); ab.flashlight(); ab.systemButtons(); ab.audio.begin(); ab.waitNoButtons();
  ab.setFrameRate(60);
  randomSeed(ab.generateRandomSeed());
  for (uint8_t k = 0; k < 44; k++) { bool top = k < 20; stars[k][0] = top ? k * 12 + random(12) : (k - 20) * 10 + random(10); stars[k][1] = top ? random(1, 17) : random(17, 50); }   // spread evenly across the sky, extra up where the planes fly
  loadBest();
  FX::begin(FX_DATA_PAGE);
}

// points around the saucer (upright, centre at 0,0) that must stay clear
const int8_t HITPTS[][2] PROGMEM = {{-9, 0}, {9, 0}, {-7, -1}, {7, -1}, {-6, 2}, {6, 2}, {0, 3}, {-3, -3}, {3, -3}, {0, -4}};
// exact check: does the saucer's picture overlap anything solid in the course?
uint8_t saucerFrame() { return (uint8_t)(((ra + 320) * 64 + 160) / 320 % 64) * 2; }
bool hitLevel() {
  int16_t sx0 = (int16_t)rx - 12, sy0 = (int16_t)ry - 12;
  uint32_t col[24];
  uint24_t sp = FX_UFOROT + 4 + (uint24_t)saucerFrame() * 144;
  for (uint8_t p = 0; p < 3; p++) {                                         // the saucer's own mask, 24 rows per column
    FX::seekData(sp + p * 48);
    for (uint8_t i = 0; i < 24; i++) { FX::readPendingUInt8(); uint32_t m = FX::readPendingUInt8(); if (p == 0) col[i] = m; else col[i] |= m << (p * 8); }
    FX::readEnd();
  }
  int8_t p0 = (sy0 + 64) / 8 - 8, p1 = (sy0 + 23 + 64) / 8 - 8;
  uint32_t lv[24]; for (auto& v : lv) v = 0;
  for (int8_t p = p0; p <= p1; p++) {                                       // the course's solid mask over the same spot
    int8_t sh = p * 8 - sy0;
    if (p < 0) continue;
    if (p > 7) { for (auto& v : lv) v |= sh >= 0 ? (uint32_t)0xFF << sh : 0xFFUL >> -sh; continue; }
    int16_t xa = sx0 < 0 ? 0 : sx0;
    FX::seekData(FX_LVL + ((uint24_t)p * LVL_W + xa) * 2);
    for (int16_t i = xa - sx0; i < 24; i++) {
      FX::readPendingUInt8(); uint32_t mk = FX::readPendingUInt8();
      lv[i] |= sh >= 0 ? mk << sh : mk >> -sh;
    }
    FX::readEnd();
  }
  for (uint8_t i = 0; i < 24; i++) if (col[i] & lv[i]) return true;
  return false;
}
// the mothership: checked pixel by pixel against its picture, except the open bay
bool hitMother() {
  int16_t sx0 = (int16_t)rx - 12, sy0 = (int16_t)ry - 12;
  if (sx0 + 24 <= MS_L || msRise > 0) return false;
  uint32_t col[24];
  uint24_t sp = FX_UFOROT + 4 + (uint24_t)saucerFrame() * 144;
  for (uint8_t p = 0; p < 3; p++) {
    FX::seekData(sp + p * 48);
    for (uint8_t i = 0; i < 24; i++) { FX::readPendingUInt8(); uint32_t m = FX::readPendingUInt8(); if (p == 0) col[i] = m; else col[i] |= m << (p * 8); }
    FX::readEnd();
  }
  int8_t p0 = (sy0 + 64) / 8 - 8, p1 = (sy0 + 23 + 64) / 8 - 8;
  for (uint8_t i = 0; i < 24; i++) {
    int16_t bx = sx0 + i - MS_L; if (bx < 0 || bx >= 130) continue;
    uint32_t lv = 0;
    for (int8_t p = p0; p <= p1; p++) {
      if (p < 0 || p > 7) continue;
      int8_t sh = p * 8 - sy0; uint8_t mk; FX::readDataBytes(FX_MOTHER + 4 + ((uint24_t)p * 130 + bx) * 2 + 1, &mk, 1);
      lv |= sh >= 0 ? (uint32_t)mk << sh : (uint32_t)mk >> -sh;
    }
    if (bx >= MOUTH - 4 && bx <= BAY_R) for (int8_t y = BAY_T; y <= BAY_B; y++) { int8_t r = y - sy0; if (r >= 0 && r < 24) lv &= ~(1UL << r); }   // bay is open
    if (col[i] & lv) return true;
  }
  return false;
}
// a random insult on the end screen: crash lines first, then lines for when you escape
const char J0A[] PROGMEM = "GLORBON, WE HAVE"; const char J0B[] PROGMEM = "A PROBLEM!";
const char J1A[] PROGMEM = "GIB GLORB GLOMMIT!"; const char J1B[] PROGMEM = "";
const char J2A[] PROGMEM = "ROSWELL HAD A BETTER"; const char J2B[] PROGMEM = "LANDING THAN THAT.";
const char J3A[] PROGMEM = "HAVE ANOTHER DRINK."; const char J3B[] PROGMEM = "";
const char J4A[] PROGMEM = "CROP CIRCLE? NO."; const char J4B[] PROGMEM = "THAT'S A CRATER.";
const char J5A[] PROGMEM = "YOUR SAUCER IS NOW"; const char J5B[] PROGMEM = "A BROKEN FRISBEE.";
const char J6A[] PROGMEM = "THE FARMER IS"; const char J6B[] PROGMEM = "LAUGHING AT YOU.";
const char J7A[] PROGMEM = "ELON WANTS TO HIRE"; const char J7B[] PROGMEM = "YOU. AS A TEST DUMMY.";
const char J8A[] PROGMEM = "THE MOTHERSHIP LEFT"; const char J8B[] PROGMEM = "WITHOUT YOU. AGAIN.";
const char J9A[] PROGMEM = "YOU FLY LIKE A"; const char J9B[] PROGMEM = "STORMTROOPER AIMS.";
const char J10A[] PROGMEM = "WARP SPEED INTO A"; const char J10B[] PROGMEM = "WALL IS STILL A WALL.";
const char J11A[] PROGMEM = "NASA CALLED. THEY'RE"; const char J11B[] PROGMEM = "NOT HIRING.";
const char J12A[] PROGMEM = "GRAVITY 1"; const char J12B[] PROGMEM = "EARTHLING 0";
const char J13A[] PROGMEM = "GLORB'S MOM PARKS"; const char J13B[] PROGMEM = "BETTER THAN THAT.";
const char J14A[] PROGMEM = "AREA 51 IS FILING"; const char J14B[] PROGMEM = "THAT UNDER: OOPS.";
const char J15A[] PROGMEM = "EVEN THE COWS SAW"; const char J15B[] PROGMEM = "THAT COMING.";
const char J16A[] PROGMEM = "SPACEBALLS!"; const char J16B[] PROGMEM = "";
const char J17A[] PROGMEM = "DINNER PLATE DOWN!"; const char J17B[] PROGMEM = "";
const char J18A[] PROGMEM = "GLORB IS PROUD."; const char J18B[] PROGMEM = "AND A LITTLE SHOCKED.";
const char J19A[] PROGMEM = "BEAM ME UP, BUDDY!"; const char J19B[] PROGMEM = "YOU DID IT!";
const char J20A[] PROGMEM = "BEST PILOT IN THE"; const char J20B[] PROGMEM = "GALAXY. TODAY, ANYWAY!";
const char J21A[] PROGMEM = "EMPLOYEE OF THE MONTH!"; const char J21B[] PROGMEM = "";
const char J22A[] PROGMEM = "SMOOTH! GLORB OWES"; const char J22B[] PROGMEM = "YOU A SPACE PIZZA.";
const char J23A[] PROGMEM = "WELCOME HOME, ACE!"; const char J23B[] PROGMEM = "";
const char J24A[] PROGMEM = "HOUSTON, WE HAVE"; const char J24B[] PROGMEM = "NO PROBLEMS!";
const char J25A[] PROGMEM = "ONE GIANT LEAP FOR"; const char J25B[] PROGMEM = "GLORB-KIND!";
const char* const JOKES[][2] PROGMEM = {{J0A, J0B}, {J1A, J1B}, {J2A, J2B}, {J3A, J3B}, {J4A, J4B}, {J5A, J5B}, {J6A, J6B}, {J7A, J7B}, {J8A, J8B}, {J9A, J9B}, {J10A, J10B}, {J11A, J11B}, {J12A, J12B}, {J13A, J13B}, {J14A, J14B}, {J15A, J15B}, {J16A, J16B}, {J17A, J17B}, {J18A, J18B}, {J19A, J19B}, {J20A, J20B}, {J21A, J21B}, {J22A, J22B}, {J23A, J23B}, {J24A, J24B}, {J25A, J25B}};
const uint8_t N_CRASH = 18, N_WIN = 8;
uint8_t joke;
uint8_t winStage; uint16_t glT;                                           // after escaping: 0 fly-off, 1 Glorb talks, 2 score
void endRun(uint8_t how) {
  fst = how; endT = 0;
  joke = how == F_WIN ? N_CRASH + random(N_WIN) : random(N_CRASH);
  winStage = 0; glT = 0;
  if (how == F_WIN) {
    int32_t tb = 18000L - (int32_t)flyT;                                   // time bonus: 1 point for every frame under 5 minutes
    uint8_t pct = flyT ? (uint32_t)fuelT * 100 / flyT : 0;
    dist = (MS_L + BAY_R - START_X) * 5L / 2;
    score = 5000 + stunts() + (tb > 0 ? tb : 0) + (uint32_t)(100 - pct) * 100;   // 5000 for escaping, 100 per % of fuel saved
  } else score = stunts();
  if (score > bestScore) { bestScore = score; newBest = true; }
  if (dist > best) best = dist;
  saveBest();
  if (how == F_CRASH) {
    shakeT = 18; burst(rx, ry); snd.tone(NOTE_C3, 80, NOTE_A2, 120);
    for (uint8_t k = 0; k < 6; k++) {                                       // the saucer breaks apart
      float dir = k == 0 ? 0 : (k & 1 ? -1 : 1);
      deb[k] = {rx, ry, vx * 0.4f + dir * (0.4f + random(60) / 100.0f), (k == 0 ? -1.6f : -0.6f - random(80) / 100.0f), ra * TURN, (float)(random(30) - 15) / 60, (uint8_t)(k < 3 ? k : 3)};
    }
  }
  else snd.tone(NOTE_C5, 80, NOTE_E5, 80, NOTE_G5, 160);
}

// ------------------------------------------------------------------ air traffic along the top
// Each part of the course has its own things flying right-to-left near the top of the screen.
enum { A_BIRD, A_PLANE, A_HELI, A_BLIMP, A_BALLOON, A_GULL, A_JET, NA_ };
const int8_t AIR_HW[NA_] PROGMEM = {3, 8, 8, 16, 5, 4, 8};        // half width of what you can hit
const int8_t AIR_HH[NA_] PROGMEM = {2, 3, 4, 6, 7, 2, 2};         // half height
const int8_t AIR_SP[NA_] PROGMEM = {-12, -18, -14, -6, -4, -14, -30};   // speed in 1/32 px per frame
// where each part of the course starts, and what flies there (two choices each)
const int16_t SEC_X[] PROGMEM = {0, 950, 1110, 1690, 1900, 2900, 3700, 4400, 5400, 6150, 7050};   // 1110-1690 is the tunnel
const uint8_t SEC_AIR[][2] PROGMEM = {{A_BIRD, A_BIRD}, {A_BIRD, A_PLANE}, {255, 255}, {A_BIRD, A_PLANE}, {A_PLANE, A_BIRD}, {A_PLANE, A_HELI},
                                      {A_BALLOON, A_BLIMP}, {A_HELI, A_PLANE}, {A_GULL, A_PLANE}, {255, 255}, {A_JET, A_HELI}};
void spawnAir() {
  int16_t sx = (int16_t)camx + 128; uint8_t s = 0;
  for (uint8_t k = 0; k < 11; k++) if (sx >= (int16_t)pgm_read_word(&SEC_X[k])) s = k;
  uint8_t kind = pgm_read_byte(&SEC_AIR[s][random(2)]);
  if (kind == 255 || sx > LVL_W - 200) return;                      // nothing in the cave or at the very end
  if (kind == A_BALLOON || kind == A_BLIMP) {                         // never more than two big floaty things at once
    uint8_t n = 0; for (auto& a : air) if (a.on && (a.kind == A_BALLOON || a.kind == A_BLIMP)) n++;
    if (n >= 2) kind = A_BIRD;
  }
  uint8_t on = 0; for (auto& a : air) if (a.on) on++;
  if (on >= 2) return;                                                // never more than two things in the sky at once
  for (auto& a : air) if (!a.on) {                                    // one at a time, no flocks
    float y = kind == A_BLIMP ? 7 : kind == A_BALLOON ? 9 : (kind == A_BIRD || kind == A_GULL) ? 3 + random(6) : 5 + random(4);   // whole picture stays on screen
    a = {(float)(sx + 12), y, kind, (uint8_t)random(255), true}; break;
  }
}
void updateAir() {
  if (fst == F_FLY) {
    if (airT) airT--;
    else { spawnAir(); int16_t iv = 330 - (int16_t)(rx / 65); if (iv < 210) iv = 210; airT = iv / 2 + random(iv); }   // random gaps, about 5.5 s apart at the start, 3.5 s near the end
  }
  for (auto& a : air) if (a.on) {
    a.t++; a.x += (int8_t)pgm_read_byte(&AIR_SP[a.kind]) / 32.0f;
    if (a.kind == A_GULL || a.kind == A_HELI) a.y += sin(a.t * 0.08f) * 0.08f;
    if (a.kind == A_BALLOON) a.y += sin(a.t * 0.03f) * 0.02f;
    if (a.x < camx - 40) a.on = false;
  }
}
bool hitAir(float px, float py) {
  for (auto& a : air) if (a.on && fabs(px - a.x) < (int8_t)pgm_read_byte(&AIR_HW[a.kind]) && fabs(py - a.y) < (int8_t)pgm_read_byte(&AIR_HH[a.kind])) return true;
  return false;
}
void drawAir() {
  for (auto& a : air) if (a.on) {
    int16_t x = SX(a.x), y = a.y; uint8_t f = (a.t >> 3) & 1;
    if (x < -40 || x > 170) continue;
    switch (a.kind) {
      case A_BIRD: case A_GULL: {                                   // flapping V
        int8_t w = a.kind == A_GULL ? 4 : 3, d = f ? -2 : 1;
        ab.drawLine(x - w, y + d, x, y, WHITE); ab.drawLine(x, y, x + w, y + d, WHITE); break; }
      case A_PLANE:                                                  // little prop plane, flying left
        frect(x - 7, y - 1, 14, 3, BLACK); ab.drawRoundRect(x - 7, y - 1, 14, 3, 1, WHITE);
        ab.drawLine(x + 3, y - 1, x + 7, y - 4, WHITE); ab.drawLine(x + 7, y - 4, x + 7, y - 1, WHITE);   // tail
        ab.drawFastHLine(x - 3, y + 2, 6, WHITE);                                                      // wing
        ab.drawFastVLine(x - 8, y - 2 + f, 3, WHITE); ab.drawPixel(x - 4, y, BLACK); break;              // prop, window
      case A_HELI:
        frect(x - 4, y - 2, 8, 5, BLACK); ab.drawRoundRect(x - 4, y - 2, 8, 5, 2, WHITE);
        ab.drawFastHLine(x + 4, y, 6, WHITE); ab.drawFastVLine(x + 9, y - 2 + f, 3, WHITE);              // tail and rotor
        ab.drawFastVLine(x, y - 4, 2, WHITE); ab.drawFastHLine(f ? x - 8 : x - 5, y - 4, f ? 16 : 10, WHITE);
        ab.drawFastHLine(x - 3, y + 4, 7, WHITE); ab.drawPixel(x - 2, y - 1, WHITE); break;
      case A_BLIMP:
        frect(x - 15, y - 5, 30, 10, BLACK); ab.drawRoundRect(x - 15, y - 5, 30, 10, 5, WHITE);
        for (int8_t k = -9; k < 10; k += 3) ab.drawPixel(x + k, y - 1, WHITE);
        ab.drawLine(x + 12, y - 3, x + 17, y - 6, WHITE); ab.drawLine(x + 12, y + 3, x + 17, y + 6, WHITE);
        frect(x - 3, y + 5, 6, 2, WHITE); break;
      case A_BALLOON:
        frect(x - 5, y - 8, 11, 11, BLACK); ab.drawCircle(x, y - 3, 5, WHITE);
        ab.drawFastVLine(x, y - 8, 10, WHITE); ab.drawLine(x - 4, y, x - 2, y + 4, WHITE); ab.drawLine(x + 4, y, x + 2, y + 4, WHITE);
        frect(x - 2, y + 5, 5, 3, WHITE); break;
      case A_JET:
        frect(x - 8, y - 1, 16, 3, BLACK); ab.drawLine(x - 8, y, x + 7, y - 1, WHITE); ab.drawLine(x - 8, y, x + 7, y + 1, WHITE);
        ab.drawLine(x + 2, y, x + 6, y - 4, WHITE); ab.drawFastVLine(x + 7, y - 2, 4, WHITE);
        if (f) { ab.drawPixel(x + 10, y, WHITE); ab.drawPixel(x + 13, y, WHITE); } break;
    }
  }
}


// ------------------------------------------------------------------ fireworks over the highway (just for show, can't hit you)
const int16_t FW_A = 3000, FW_B = 3600;                                     // where the show is
uint8_t fwT;
void updateFireworks() {
  if (fwT) fwT--;
  else if (camx > FW_A - 128 && camx < FW_B) {
    for (auto& f : fw) if (!f.t) { f = {(int16_t)(camx + 40 + random(110)), (int8_t)(18 + random(14)), 1}; fwT = 25 + random(30); break; }
  }
  for (auto& f : fw) if (f.t) { if (++f.t > 90) f.t = 0; if (f.t == 31) snd.tone(150 + random(60), 25); }
}
void drawFireworks() {
  for (auto& f : fw) if (f.t) {
    int16_t x = SX(f.x);
    if (f.t <= 30) {                                                         // rocket climbing with a sparkly trail
      int16_t y = GROUND - 2 - (GROUND - 2 - f.top) * f.t / 30;
      ab.drawPixel(x, y, WHITE); if (f.t & 1) ab.drawPixel(x, y + 2, WHITE);
    } else {                                                                 // burst: a ring of sparks spreading and drooping
      uint8_t t = f.t - 30;
      if (t > 40 && (t & 1)) continue;                                       // flicker out at the end
      for (uint8_t k = 0; k < 16; k++) {                                     // outer ring of 16 sparks, inner ring at half size
        float a = k * 0.3927f, r = t * 0.45f; if (r > 14) r = 14;
        if (k & 1) r *= 0.55f;
        float dx = cos(a) * r, dy = sin(a) * r + t * t / 220;
        ab.drawPixel(x + dx, f.top + dy, WHITE);
        if (t < 24 && !(k & 1)) ab.drawPixel(x + dx * 0.8f, f.top + dy * 0.8f, WHITE);   // short streak while it opens
      }
    }
  }
}

void updatePlay() {
  playT++;
  bool Lb = ab.pressed(LEFT_BUTTON), Rb = ab.pressed(RIGHT_BUTTON);
  bool btn = ab.pressed(B_BUTTON);                                          // outer button: booster
  if (lock && !btn) lock = false;
  thr = btn && !lock && fst <= F_FLY;
  if (fst == F_READY && thr) { fst = F_FLY; snd.tone(NOTE_C4, 40, NOTE_G4, 40); }
  if (fst == F_FLY) {
    float before = raF;
    if (ab.justPressed(A_BUTTON)) {                                          // inner button: quarter turn anticlockwise to 12, 9, 6 or 3 o'clock
      if (spinning) spinTo -= 80;                                            // pressing again mid-turn stacks another quarter
      else if (raF > 0.5f && raF < 80) spinTo = -80;                         // leaning right: first click goes straight to 9 o'clock,
      else spinTo = floor((raF - 0.5f) / 80) * 80;                          // so 4 clicks is always a full turn back to upright
      spinning = true; snd.tone(NOTE_E5, 15);
    }
    if (spinning) { raF -= 20; if (raF <= spinTo) { raF = spinTo; spinning = false; } }   // 4 frames per quarter turn
    else { if (Lb) raF -= TURN_SPEED; if (Rb) raF += TURN_SPEED; }
    spinAcc += raF - before;                                                 // full turn either way = bonus
    if (spinAcc >= 320 || spinAcc <= -320) { spinAcc = 0; flips++; popT = 50; pop720 = 0; snd.tone(NOTE_C6, 40, NOTE_G6, 60); }
    if (thr) { coastAcc = 0; got720 = false; } else coastAcc += raF - before;                    // two full turns without touching the booster
    if (coastAcc >= 960 || coastAcc <= -960) { coastAcc = 0; big1080++; big720--; got720 = false; popT = 90; pop720 = 2; snd.tone(NOTE_C6, 60, NOTE_G6, 60, NOTE_C7, 220); }   // three turns without the booster: the 720 becomes a 1080
    else if ((coastAcc >= 640 || coastAcc <= -640) && !got720) { got720 = true; big720++; popT = 70; pop720 = 1; snd.tone(NOTE_C6, 60, NOTE_E6, 60, NOTE_C7, 160); }
    if (raF >= 160) { raF -= 320; spinTo -= 320; } if (raF < -160) { raF += 320; spinTo += 320; }
    ra = (int16_t)(raF < 0 ? raF - 0.5f : raF + 0.5f);
    float s = sin(ra * TURN), c = cos(ra * TURN);
    vy += GRAV;
    if (thr) { vx += THRUST * s; vy -= THRUST * c; }
    vx *= DRAG_X; vy *= DRAG_Y;
    if (vy > 1.6f) vy -= 0.04f; if (vy < -2) vy = -2;                   // speed limits like the rocket
    if (vx > 4) vx = 4; if (vx < -4) vx = -4;
    rx += vx; ry += vy;
    if (ry < 4) { ry = 4; if (vy < 0) vy = 0; }                              // top of the sky
    if (rx < camx + 12) { rx = camx + 12; if (vx < 0) vx = 0; }              // can't go back off screen
    if (legs > 0) legs -= 0.2f; if (legs < 0) legs = 0;                     // legs tuck away after takeoff
    flyT++; if (thr) fuelT++;
    if (ra > 120 || ra < -120) upT++;                                        // upside down
    int16_t d = (int16_t)((rx - START_X) * 2.5f); if (d > (int16_t)dist) dist = d;   // 4 pixels = 1 metre, kept in tenths
    // touching anything?
    bool hitBody = hitLevel();                                             // pixel-exact against the scenery
    for (uint8_t k = 0; k < 10 && !hitBody; k++) {
      int8_t lx = pgm_read_byte(&HITPTS[k][0]), ly = pgm_read_byte(&HITPTS[k][1]);
      float hx = rx + lx * c - ly * s, hy = ry + lx * s + ly * c;
      hitBody = hitAir(hx, hy);
    }
    if (!hitBody && !(rx > MS_L + MOUTH - 34 && ry < 46)) hitBody = hitMother();                                     // the mothership's hull and legs count too
    if (rx > MS_L + MOUTH - 34 && ry < 46) { hitBody = false; vx = vy = 0; endRun(F_WIN); }   // close enough: the tractor beam grabs you
    else if (hitBody) endRun(F_CRASH);
  } else if (fst >= F_CRASH) {
    bool press = ab.justPressed(A_BUTTON) || ab.justPressed(B_BUTTON);
    if (endT < 250) endT++;
    if (fst == F_CRASH) { if (endT > 80 && press) newGame(); }
    else if (winStage == 0) { if (endT >= 150) { winStage = 1; glT = 0; snd.noTone(); } }
    else if (winStage == 1) { glT++; if (press && glT > 10) { if (glT < 380) glT = 380; else { winStage = 2; glT = 0; } } }
    else { if (glT < 400) glT++; if (press) { if (glT < 140) glT = 140; else if (glT > 150) newGame(); } }
    if (fst == F_WIN) {                                                       // pulled inside, door shuts, up and away
      if (endT < 40) { rx += (MS_L + BAY_R - 12 - rx) * 0.08f; ry += ((BAY_T + BAY_B) / 2 - ry) * 0.15f; raF *= 0.85f; ra = (int16_t)raF; }   // pulled in
      if (endT == 60) snd.tone(NOTE_C3, 60, NOTE_C2, 80);
      if (endT > 70 && msRise < 90) { msRise += (endT - 70) * 0.02f; if ((endT & 3) == 0) snd.tone(200 + endT * 6, 20); }
    }
  }
  // booster: waves pushed out from under the saucer
  if (thr && fst == F_FLY && (playT % 4) == 0) {
    float s = sin(ra * TURN), c = cos(ra * TURN);
    for (auto& w : wave) if (!w.t) { w = {rx - s * 4, ry + c * 4, -s, c, 11}; break; }
    if ((playT % 8) == 0) snd.tone(120 + random(40), 20);
  }
  for (auto& w : wave) if (w.t) w.t--;
  if (popT) popT--;
  for (auto& s : spark) if (s.t) { s.t--; if ((s.t & 1) == 0) { s.x += s.vx / 6; s.y += s.vy / 6; s.vy += 2; } if (s.y > 62) s.y = 62; }
  for (auto& d : deb) if (d.k != 255) {                                     // pieces tumble, bounce and settle
    d.vy += 0.07f; d.x += d.vx; d.y += d.vy; d.a += d.va;
    if (solid((int16_t)d.x, (int16_t)d.y + 1)) { d.y -= d.vy; d.vy = d.vy > 0.4f ? -d.vy * 0.45f : 0; d.vx *= 0.7f; d.va *= 0.6f; }
  }
  updateAir(); updateFireworks();
  float want = rx - 44; if (want < camx) want = camx; if (want > LVL_W - 128) want = LVL_W - 128;
  camx += (want - camx) * 0.25f;
  if (shakeT) shakeT--;
}

void drawLevel() {                                     // sky, then the course from FX on top (its mask hides the stars)
  for (auto& s : stars) { int16_t x = (s[0] - (int16_t)(camx / 6)) & 255; if (x < 128 && ((playT >> 4) + s[1]) % 9) ab.drawPixel(x, s[1], WHITE); }
  int16_t cx = (int16_t)camx;
  for (uint8_t p = 0; p < 8; p++) {                    // one read per row: picture byte, solid byte, picture byte...
    uint8_t* row = ab.sBuffer + p * 128;
    FX::seekData(FX_LVL + ((uint24_t)p * LVL_W + cx) * 2);
    for (uint8_t i = 0; i < 128; i++) { uint8_t im = FX::readPendingUInt8(), mk = FX::readPendingUInt8(); row[i] = (row[i] & ~mk) | im; }
    FX::readEnd();
  }
  int16_t bx = START_X + best * 2 / 5 - cx;                // your best so far: a dotted line across the sky
  if (best && bx > 0 && bx < 128) { for (uint8_t y = 8; y < 56; y += 3) ab.drawPixel(bx, y, WHITE); tinyS(bx + 2, 8, PSTR("BEST")); }
}

void drawMother() {
  int16_t x = SX(MS_L), y = -(int16_t)msRise;
  if (x > 127 || y < -64) return;
  FX::drawBitmap(x, y, FX_MOTHER, 0, dbmMasked);
  int16_t cy = y + (BAY_T + BAY_B) / 2;
  if (fst == F_FLY) {                                                        // big arrows sliding into the mouth: FLY IN HERE
    for (int8_t k = 0; k < 3; k++) {
      int16_t ax = x + MOUTH - 44 + k * 12 + (playT >> 1) % 12;
      for (int8_t w = 0; w < 2; w++) { ab.drawLine(ax + w, cy - 5, ax + 5 + w, cy, WHITE); ab.drawLine(ax + 5 + w, cy, ax + w, cy + 5, WHITE); }
    }
    if (playT & 16) { frect(x + MOUTH - 57, cy - 15, 50, 7, BLACK); tinyS(x + MOUTH - 55, cy - 14, PSTR("GET IN LOSER")); }
  }
  if (fst == F_WIN && endT < 44) {                                           // tractor beam pulling you in
    int16_t sx = SX(rx);
    for (int16_t bxx = sx; bxx < x + BAY_R; bxx += 3) { int8_t o = ((bxx + endT) % 6) < 3; ab.drawPixel(bxx, cy - 7 + o, WHITE); ab.drawPixel(bxx, cy + 7 - o, WHITE); }
  }
  for (int8_t k = 0; k < 4; k++) if (((playT >> 3) & 3) == k) {           // arrows in the bay blink inward
    int16_t ax = x + BAY_L + 6 + k * 9, ay = y + (BAY_T + BAY_B) / 2;
    ab.drawLine(ax, ay - 3, ax + 3, ay, WHITE); ab.drawLine(ax + 3, ay, ax, ay + 3, WHITE);
  }
  for (int16_t k = x + BAY_R + 8; k < 128; k += 6) if (((k - x) / 6 + (playT >> 3)) % 3 == 0) frect(k, y + 24, 2, 2, WHITE);   // running lights on the rim
  if (fst == F_WIN && endT > 40) {                                          // hangar door slides shut from top and bottom
    uint8_t h = endT > 60 ? (BAY_B - BAY_T) / 2 + 1 : (endT - 40) * ((BAY_B - BAY_T) / 2 + 1) / 20;
    frect(x + BAY_L - 1, y + BAY_T, 3, h, WHITE); frect(x + BAY_L - 1, y + BAY_B + 1 - h, 3, h, WHITE);
    ab.drawFastVLine(x + BAY_L + 2, y + BAY_T, h, BLACK);
  }
}

void drawDebris() {
  if (fst == F_CRASH && endT < 8) ab.drawCircle(SX(deb[0].x - deb[0].vx * endT), (int16_t)ry, endT * 2 + 2, WHITE);   // blast ring
  for (auto& d : deb) if (d.k != 255) {
    int16_t x = SX(d.x), y = d.y; float c = cos(d.a), sn = sin(d.a);
    if (d.k == 0) { for (int8_t t = 0; t <= 6; t++) { float q = d.a + t * 0.52f; ab.drawPixel(x + 3 * cos(q), y - 3 * sin(q), WHITE); } ab.drawLine(x - 3 * c, y - 3 * sn, x + 3 * c, y + 3 * sn, WHITE); }   // dome
    else { int8_t L = d.k == 3 ? 2 : 5;                                    // disc halves and little chunks
      ab.drawLine(x - L * c, y - L * sn, x + L * c, y + L * sn, WHITE);
      if (d.k != 3) ab.drawLine(x - L * c, y - L * sn + 1, x + L * c, y + L * sn + 1, WHITE); }
  }
}

void drawSaucer() {
  for (auto& w : wave) if (w.t && (w.t > 3 || (w.t & 1))) {          // an arc that gets bigger the further it goes
    float r = 1.5f + (11 - w.t) * 0.45f;
    int8_t n = r * 0.7f;
    for (int8_t k = -n; k <= n; k++) {                                   // about one dot per pixel along the arc
      float a = k / r, ca = 1 - a * a * 0.5f, sa = a;                  // cheap curve, no trig
      float dx = (w.ex * ca - w.ey * sa) * r, dy = (w.ey * ca + w.ex * sa) * r;
      ab.drawPixel(SX(w.x + dx), (int16_t)(w.y + dy), WHITE);
    }
  }
  float s = sin(ra * TURN), c = cos(ra * TURN);
  if (thr && fst == F_FLY) {                                               // glow right under the saucer
    int16_t gx = SX(rx - s * 5), gy = ry + c * 5;
    ab.drawPixel(gx, gy, WHITE); if (playT & 2) { ab.drawPixel(gx - 1, gy + 1, WHITE); ab.drawPixel(gx + 1, gy + 1, WHITE); }
  }
  if (fst != F_CRASH && !(fst == F_WIN && endT > 44)) {
    if (legs > 0.3f) for (int8_t sx = -1; sx <= 1; sx += 2) {               // landing legs
      float ax = sx * 5, ay = 3, fx = sx * 8, fy = 3 + legs;
      int16_t x0 = SX(rx + ax * c - ay * s), y0 = ry + ax * s + ay * c, x1 = SX(rx + fx * c - fy * s), y1 = ry + fx * s + fy * c;
      ab.drawLine(x0, y0, x1, y1, WHITE); ab.drawLine(x1 - 1, y1, x1 + 1, y1, WHITE);
    }
    FX::drawBitmap(SX(rx) - 12, (int16_t)ry - 12, FX_UFOROT, saucerFrame() + ((playT >> 3) & 1), dbmMasked);
  }
  for (auto& s : spark) if (s.t && (s.t > 8 || (s.t & 1))) ab.drawPixel(SX(s.x), s.y, WHITE);
}

void drawHud() {
  { int16_t e = tinyN(1, 1, dist / 10); tinyS(e, 1, PSTR("M")); }             // distance so far, in metres
  if (popT) { int16_t px = SX(rx) - 12, py = (int16_t)ry - 18 + popT / 8; frect(px - 1, py - 1, pop720 == 2 ? 60 : 34, 7, BLACK); int16_t e = tinyS(px, py, pop720 == 2 ? PSTR("1080!!! +") : pop720 ? PSTR("720!! +") : PSTR("360! +")); tinyN(e, py, pop720 == 2 ? 5000 : pop720 ? 2000 : 500); }
  bool show = fst == F_CRASH ? endT > 40 : fst == F_WIN && winStage == 2;
  if (show) {
    showScreen(FX_SCOREBG);                                                 // framed panel
    frect(3, 2, 122, 13, BLACK);                                            // insult sits up top
    for (uint8_t k = 0; k < 2; k++) {
      PGM_P t = (PGM_P)pgm_read_ptr(&JOKES[joke][k]);
      bool one = !pgm_read_byte((PGM_P)pgm_read_ptr(&JOKES[joke][1]));          // one-liners sit in the middle
      tinyS(64 - (int16_t)strlen_P(t) * 2, one ? 6 : 3 + k * 6, t);
    }
    tinyS(52, 18, PSTR("POINTS"));
    uint32_t v = score;                         // the score, big, in the middle
    if (fst == F_WIN && glT < 40) { v = v * glT / 40; if (glT & 1) snd.tone(300 + glT * 20, 15); }
    if (fst == F_WIN && glT == 40) snd.tone(NOTE_C5, 80, NOTE_E5, 80, NOTE_G5, 200);
    { char b[10]; uint8_t n = 0; do { b[n++] = '0' + v % 10; v /= 10; } while (v);
      int16_t x = 64 - (n * 12 - 2) / 2;
      while (n) { uint8_t g = b[--n] - 32;
        for (uint8_t i = 0; i < 5; i++) { uint8_t c = pgm_read_byte(FONT + g * 5 + i); for (uint8_t j = 0; j < 7; j++) if (c >> j & 1) frect(x + i * 2, 24 + j * 2, 2, 2, WHITE); }
        x += 12; } }
    { uint8_t d = 1; for (uint16_t k = dist / 10; k >= 10; k /= 10) d++;   // distance under it
      at(64 - (d + 12) * 3, 43); PS("DISTANCE "); pn(dist / 10); pc('.'); pn(dist % 10); pc('M'); }
    if (newBest && (fst == F_CRASH || glT >= 40) && (playT & 8)) tinyS(46, 51, PSTR("NEW BEST!"));
    if (fst == F_WIN && glT >= 40) {
      if (flyT < 150 * 60) {                                                 // medal: gold, silver or bronze by time
        ab.drawCircle(112, 30, 6, WHITE); ab.drawCircle(112, 30, 5, WHITE);
        at(110, 27); pc(flyT < 70 * 60 ? 'G' : flyT < 100 * 60 ? 'S' : 'B');
      }
    }
    if ((fst == F_CRASH ? endT > 80 : glT > 150) && (playT & 32)) tinyS(36, 57, PSTR("PRESS TO RETRY"));
  }
}



const char G0[] PROGMEM = "\"I MESSED WITH"; const char G1[] PROGMEM = "THE WRONG"; const char G2[] PROGMEM = "DAIRY FARMER!";
const char G3[] PROGMEM = "WE GOTTA GET"; const char G4[] PROGMEM = "BACK TO THE"; const char G5[] PROGMEM = "MOTHERSHIP!\"";
const char* const GLINES[] PROGMEM = {G0, G1, G2, G3, G4, G5};
// what Glorb says when you make it home
const char W0[] PROGMEM = ""; const char W1[] PROGMEM = "\"LOL, WE GOT"; const char W2[] PROGMEM = "AWAY...";
const char W3[] PROGMEM = "NOW LET'S GO"; const char W4[] PROGMEM = "MESS WITH"; const char W5[] PROGMEM = "HUBBLE\"";
const char* const WLINES[] PROGMEM = {W0, W1, W2, W3, W4, W5};
void glorbWords(const char* const* lines, uint16_t clock) {
  uint8_t idx = 0;
  for (uint8_t l = 0; l < 6; l++) {
    PGM_P s = (PGM_P)pgm_read_ptr(&lines[l]);
    uint8_t n = strlen_P(s); int16_t wid = -1;
    for (uint8_t k = 0; k < n; k++) { char q = pgm_read_byte(s + k); wid += (q == 'M' || q == 'W') ? 6 : q == ' ' ? 3 : 4; }   // M and W are drawn wide, spaces narrow
    int16_t x = 96 - wid / 2, y = 4 + l * 7;
    for (uint8_t k = 0; k < n; k++) {
      char c = pgm_read_byte(s + k);
      bool wide = c == 'M' || c == 'W'; uint8_t cw = wide ? 5 : 3;
      if (c != ' ') {
        int16_t p = (int16_t)clock - 30 - idx * 6; idx++;
        uint8_t alien[5]; uint8_t h = c * 37 + 11;
        alien[0] = alien[2] = alien[4] = (h & 27) | 17; alien[1] = alien[3] = ((h >> 3) & 14) | ((c & 1) ? 1 : 16);
        uint8_t eng[5] = {31, 2, 4, 2, 31};
        if (c == 'W') { eng[1] = 8; eng[3] = 8; }
        if (!wide) for (uint8_t i = 0; i < 3; i++) eng[i] = pgm_read_byte(TINY + tinyIdx(c) * 3 + i);
        uint8_t w = (p < 0 || p >= 12) ? cw : (uint8_t)(abs(6 - p) * cw / 6);   // squeeze to nothing and back = a spin
        if (p == 6) snd.tone(600 + (c & 15) * 30, 25);
        for (uint8_t i = 0; i < w; i++) {
          uint8_t src = i * cw / w;
          tinyCol(x + (cw - w) / 2 + i, y, p >= 6 ? eng[src] : alien[src]);
        }
      }
      x += c == ' ' ? 3 : cw + 1;
    }
  }
}

void shakeScreen() {                                       // slide the picture sideways a pixel or two
  if (!shakeT) return;
  int8_t d = (shakeT & 2) ? (shakeT > 6 ? 2 : 1) : -(shakeT > 6 ? 2 : 1);
  for (uint8_t p = 0; p < 8; p++) {
    uint8_t* row = ab.sBuffer + p * 128;
    if (d > 0) { memmove(row + d, row, 128 - d); memset(row, 0, d); }
    else { memmove(row, row - d, 128 + d); memset(row + 128 + d, 0, -d); }
  }
}

void loop() {
  if (!ab.nextFrame()) return;
  ab.pollButtons();
  bool any = ab.justPressed(A_BUTTON) || ab.justPressed(B_BUTTON);
  stT++;
  ab.clear();
  // title tune; it waits while Glorb talks, then comes back after a short pause
  bool glorbTalking = st == S_GLORB && stT < 440;
  if (st <= S_MENU && !glorbTalking) { if (!snd.playing()) snd.tones(TUNE); }
  else if (st == S_GLORB && stT == 1) snd.noTone();
  switch (st) {
    case S_TITLE:
      showScreen(FX_TITLE + (uint24_t)((stT >> 4) & 7) * 1024);
      if ((stT >> 5) & 1) tinyOutlined(33, 58, PSTR("PRESS ANY BUTTON"));    // thin black outline so the hills don't hide it
      if (any) { st = S_GLORB; stT = 0; }
      break;
    case S_GLORB:
      showScreen(FX_GLORB);
      glorbWords(GLINES, stT);
      if (any && stT > 10) { if (stT < 380) stT = 380; else { st = S_CTRL; stT = 0; } }
      break;
    case S_CTRL:
      showScreen(FX_CONTROLS);
      if (!((stT >> 5) & 1)) frect(30, 58, 68, 6, BLACK);
      if (any && stT > 10) { st = S_MENU; stT = 0; }
      break;
    case S_MENU: {
      int8_t d = ab.justPressed(RIGHT_BUTTON) - ab.justPressed(LEFT_BUTTON);
      if (d) { ab.audio.toggle(); ab.audio.saveOnOff(); }
      showScreen(FX_MENU + (uint24_t)((ab.audio.enabled() ? 0 : 2) + ((stT >> 4) & 1)) * 1024);   // picture with big SOUND ON / OFF
      if ((stT >> 5) & 1) tinyOutlined(33, 58, PSTR("PRESS ANY BUTTON"));
      if (any && stT > 10) newGame();
      break; }
    case S_PLAY:
      updatePlay();
      if (fst == F_WIN && winStage == 1) {                                 // Glorb, safe in the mothership, has something to say
        showScreen(FX_GLORB2); glorbWords(WLINES, glT);
        if (glT >= 380 && (playT & 32)) tinyOutlined(64, 57, PSTR("PRESS A BUTTON"));
        break;
      }
      drawLevel(); drawFireworks(); drawAir(); drawMother(); drawSaucer(); drawDebris(); drawHud();
      shakeScreen();
      break;
  }
  FX::display();
}
