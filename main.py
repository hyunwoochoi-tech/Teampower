import asyncio
import io
import json
import random
import string
import time
from typing import Dict, List, Optional

import qrcode
import qrcode.image.svg
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse, Response

app = FastAPI(title="Team Power Recreation Server")

AVATARS = ["🦊", "🐻", "🐼", "🐯", "🦁", "🐸", "🐙", "🦄", "🐧", "🐶", "🐱", "🐹", "🐨", "🦖", "🐝", "🐬"]

DEFAULT_QUIZZES = [
    {
        "q": "버섯은 식물이 아니라 곰팡이균(균류)이다.",
        "a": "O",
        "exp": "정답은 O! 버섯은 엽록소가 없어 광합성을 하지 못하는 '균계(곰팡이류)'에 속합니다."
    },
    {
        "q": "북극곰의 피부는 흰색이 아니라 검은색이다.",
        "a": "O",
        "exp": "정답은 O! 털은 투명(빛 반사로 희게 보임)하지만, 열을 잘 흡수하기 위해 피부 자체는 검은색입니다."
    },
    {
        "q": "바나나는 나무가 아니라 '풀(초본식물)'에서 열린다.",
        "a": "O",
        "exp": "정답은 O! 바나나는 줄기에 목질부가 없는 세계에서 가장 큰 여러해살이 풀입니다."
    },
    {
        "q": "낙지는 심장이 1개이지만, 문어는 심장이 3개다.",
        "a": "X",
        "exp": "정답은 X! 문어뿐만 아니라 낙지와 오징어 같은 두족류는 모두 심장이 3개입니다."
    },
    {
        "q": "사람의 지문처럼 고양이의 코 무늬도 개체마다 모두 다르다.",
        "a": "O",
        "exp": "정답은 O! 고양이와 강아지의 코 주름(비문)은 사람 지문처럼 세상에 단 하나뿐입니다."
    },
    {
        "q": "금성은 태양계에서 태양과 가장 가까운 행성이다.",
        "a": "X",
        "exp": "정답은 X! 태양과 가장 가까운 행성은 수성입니다. (단, 가장 뜨거운 행성은 금성!)"
    },
    {
        "q": "딸기의 겉면에 박혀 있는 깨 같은 것이 사실은 딸기의 '진짜 열매'다.",
        "a": "O",
        "exp": "정답은 O! 우리가 먹는 빨간 과육은 꽃받침이 자란 것이고, 겉의 씨처럼 보이는 게 진짜 열매(수과)입니다."
    },
    {
        "q": "오른손잡이는 왼손보다 오른손의 손톱이 더 빨리 자란다.",
        "a": "O",
        "exp": "정답은 O! 자주 사용하는 손일수록 혈액순환과 미세 자극이 활발해 손톱이 미세하게 더 빨리 자랍니다."
    },
    {
        "q": "콜라는 원래 감기약·소화제 같은 약품으로 개발되었다.",
        "a": "O",
        "exp": "정답은 O! 1886년 약사 존 펨버턴이 두통·피로 회복용 강장제로 처음 만들었습니다."
    },
    {
        "q": "남극은 육지이지만, 북극은 얼음 덩어리뿐인 바다다.",
        "a": "O",
        "exp": "정답은 O! 남극은 대륙이지만 북극은 대륙 없이 바다가 얼어 있는 북극해입니다."
    },
]


class Room:
    def __init__(self, code: str):
        self.code = code
        self.host_ws: Optional[WebSocket] = None
        self.players: Dict[str, dict] = {}
        self.player_ws: Dict[str, WebSocket] = {}
        self.current_game: str = "lobby"  # lobby, stop777, bomb, rhythm, quiz, podium
        self.quizzes: List[dict] = [dict(q) for q in DEFAULT_QUIZZES]
        self.game_state: dict = {}
        self.bg_tasks: List[asyncio.Task] = []

    def cancel_tasks(self):
        for t in self.bg_tasks:
            if not t.done():
                t.cancel()
        self.bg_tasks.clear()

    def get_public_players(self):
        return sorted(
            [
                {
                    "id": p["id"],
                    "name": p["name"],
                    "avatar": p["avatar"],
                    "score": p["score"],
                    "is_bot": p.get("is_bot", False),
                    "connected": p.get("connected", True),
                }
                for p in self.players.values()
            ],
            key=lambda x: (-x["score"], x["name"]),
        )

    def snapshot(self):
        return {
            "type": "state",
            "room": self.code,
            "current_game": self.current_game,
            "players": self.get_public_players(),
            "game_state": self.game_state,
            "quizzes_count": len(self.quizzes),
            "quizzes": self.quizzes,
        }

    async def broadcast(self, payload: Optional[dict] = None):
        data = payload if payload is not None else self.snapshot()
        text = json.dumps(data, ensure_ascii=False)
        if self.host_ws:
            try:
                await self.host_ws.send_text(text)
            except Exception:
                pass
        dead = []
        for pid, ws in list(self.player_ws.items()):
            try:
                await ws.send_text(text)
            except Exception:
                dead.append(pid)
        for pid in dead:
            self.player_ws.pop(pid, None)
            if pid in self.players:
                self.players[pid]["connected"] = False


rooms: Dict[str, Room] = {}


def generate_room_code() -> str:
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    for _ in range(100):
        code = "".join(random.choices(chars, k=4))
        if code not in rooms:
            return code
    return "".join(random.choices(chars, k=5))


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/health")
async def health():
    return {"status": "ok", "rooms": len(rooms)}


@app.get("/api/qr")
async def get_qr(data: str = Query(..., min_length=1, max_length=500)):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
    buf = io.BytesIO()
    img.save(buf)
    return Response(content=buf.getvalue(), media_type="image/svg+xml")


async def run_bot_stop777(room: Room, start_ts: float):
    try:
        bot_ids = [pid for pid, p in room.players.items() if p.get("is_bot")]
        async def single_bot(bid):
            # Bots stop around 7.77s +/- 1.8s
            target = max(3.5, random.gauss(7.77, 0.85))
            delay = (start_ts + target) - time.time()
            if delay > 0:
                await asyncio.sleep(delay)
            if room.current_game == "stop777" and room.game_state.get("phase") == "running":
                if bid not in room.game_state["results"]:
                    elapsed = round(target, 2)
                    room.game_state["results"][bid] = {
                        "time": elapsed,
                        "diff": round(abs(elapsed - 7.77), 2),
                    }
                    await room.broadcast()
        await asyncio.gather(*(single_bot(b) for b in bot_ids))
    except asyncio.CancelledError:
        pass


async def run_bomb_loop(room: Room, duration: float):
    try:
        end_ts = time.time() + duration
        room.game_state["end_ts"] = end_ts
        while time.time() < end_ts:
            if room.current_game != "bomb" or room.game_state.get("phase") != "running":
                return
            holder = room.game_state.get("holder")
            if holder and room.players.get(holder, {}).get("is_bot"):
                # Bot passes after 0.7~1.7s
                await asyncio.sleep(random.uniform(0.7, 1.6))
                if time.time() >= end_ts or room.game_state.get("phase") != "running":
                    break
                if room.game_state.get("holder") == holder:
                    others = [pid for pid in room.game_state["order"] if pid != holder]
                    if others:
                        nxt = random.choice(others)
                        room.game_state["holder"] = nxt
                        room.game_state["pass_count"] = room.game_state.get("pass_count", 0) + 1
                        room.game_state["last_pass_ts"] = time.time()
                        await room.broadcast()
            else:
                await asyncio.sleep(0.15)

        # Explode!
        if room.current_game == "bomb" and room.game_state.get("phase") == "running":
            loser = room.game_state.get("holder")
            room.game_state["phase"] = "exploded"
            room.game_state["loser"] = loser
            survivors = []
            for pid in room.game_state["order"]:
                if pid != loser and pid in room.players:
                    room.players[pid]["score"] += 50
                    survivors.append(pid)
            room.game_state["survivors"] = survivors
            await room.broadcast()
    except asyncio.CancelledError:
        pass


async def run_rhythm_loop(room: Room, duration: float = 38.0):
    try:
        bot_ids = [pid for pid, p in room.players.items() if p.get("is_bot")]
        start = time.time()
        while time.time() - start < duration:
            if room.current_game != "rhythm" or room.game_state.get("phase") != "running":
                return
            await asyncio.sleep(0.8)
            elapsed = time.time() - start
            for bid in bot_ids:
                skill = room.game_state["bot_skills"].get(bid, 1.0)
                inc = int(random.uniform(60, 140) * skill * (1 + elapsed / 40.0))
                cur = room.game_state["scores"].get(bid, {"score": 0, "combo": 0, "perfect": 0})
                cur["score"] += inc
                cur["combo"] = random.randint(3, 25)
                cur["perfect"] += random.randint(1, 3)
                room.game_state["scores"][bid] = cur
            await room.broadcast()

        if room.current_game == "rhythm" and room.game_state.get("phase") == "running":
            await finish_rhythm(room)
    except asyncio.CancelledError:
        pass


async def finish_rhythm(room: Room):
    room.game_state["phase"] = "finished"
    scores = room.game_state.get("scores", {})
    ranked = sorted(
        [(pid, scores.get(pid, {"score": 0})["score"]) for pid in room.players.keys()],
        key=lambda x: -x[1],
    )
    awards = [120, 90, 70, 50, 40]
    awarded = {}
    for idx, (pid, sc) in enumerate(ranked):
        pts = awards[idx] if idx < len(awards) else 25
        if sc == 0 and idx > 0:
            pts = 10
        room.players[pid]["score"] += pts
        awarded[pid] = pts
    room.game_state["awarded"] = awarded
    room.game_state["ranked"] = ranked
    await room.broadcast()


async def run_bot_quiz(room: Room):
    try:
        bot_ids = [pid for pid, p in room.players.items() if p.get("is_bot")]
        for bid in bot_ids:
            await asyncio.sleep(random.uniform(0.4, 1.4))
            if room.current_game != "quiz" or room.game_state.get("phase") != "open":
                return
            room.game_state["choices"][bid] = random.choice(["O", "X"])
            await room.broadcast()
        # Occasionally a bot switches mind for fun
        await asyncio.sleep(random.uniform(1.5, 3.0))
        if room.current_game == "quiz" and room.game_state.get("phase") == "open" and bot_ids:
            b = random.choice(bot_ids)
            room.game_state["choices"][b] = "X" if room.game_state["choices"].get(b) == "O" else "O"
            await room.broadcast()
    except asyncio.CancelledError:
        pass


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    role = None
    room: Optional[Room] = None
    player_id: Optional[str] = None

    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            mtype = msg.get("type")

            if mtype == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))
                continue

            # --- HOST CREATE / RECONNECT ---
            if mtype == "host_create":
                req_code = (msg.get("room") or "").strip().upper()
                if req_code and req_code in rooms:
                    room = rooms[req_code]
                else:
                    code = generate_room_code()
                    room = Room(code)
                    rooms[code] = room
                room.host_ws = ws
                role = "host"
                await ws.send_text(json.dumps(room.snapshot(), ensure_ascii=False))
                continue

            # --- PLAYER JOIN ---
            if mtype == "player_join":
                code = (msg.get("room") or "").strip().upper()
                name = (msg.get("name") or "").strip()[:12]
                avatar = msg.get("avatar") or random.choice(AVATARS)
                req_pid = msg.get("player_id")

                if code not in rooms:
                    await ws.send_text(json.dumps({"type": "error", "message": "존재하지 않는 방 코드입니다. 사회자 화면의 코드를 확인해주세요."}, ensure_ascii=False))
                    continue

                room = rooms[code]
                role = "player"

                if req_pid and req_pid in room.players:
                    player_id = req_pid
                    room.players[player_id]["connected"] = True
                    if name:
                        room.players[player_id]["name"] = name
                else:
                    if not name:
                        await ws.send_text(json.dumps({"type": "error", "message": "닉네임을 입력해주세요!"}, ensure_ascii=False))
                        continue
                    player_id = "p_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
                    room.players[player_id] = {
                        "id": player_id,
                        "name": name,
                        "avatar": avatar,
                        "score": 0,
                        "is_bot": False,
                        "connected": True,
                    }

                room.player_ws[player_id] = ws
                await ws.send_text(json.dumps({"type": "joined", "player_id": player_id, "room": code}, ensure_ascii=False))
                await room.broadcast()
                continue

            if not room:
                continue

            # --- HOST ACTIONS ---
            if role == "host":
                if mtype == "add_bot":
                    bot_names = ["김계약", "이조달", "박상생", "최발주", "정단가", "한협상", "윤견적", "서실무"]
                    existing = {p["name"] for p in room.players.values()}
                    avail = [n for n in bot_names if n not in existing]
                    bname = avail[0] if avail else f"봇{len(room.players)+1}"
                    bid = "bot_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
                    room.players[bid] = {
                        "id": bid,
                        "name": bname,
                        "avatar": random.choice(AVATARS),
                        "score": 0,
                        "is_bot": True,
                        "connected": True,
                    }
                    await room.broadcast()

                elif mtype == "remove_player":
                    pid = msg.get("player_id")
                    if pid in room.players:
                        room.players.pop(pid, None)
                        room.player_ws.pop(pid, None)
                        await room.broadcast()

                elif mtype == "reset_scores":
                    for p in room.players.values():
                        p["score"] = 0
                    await room.broadcast()

                elif mtype == "switch_game":
                    room.cancel_tasks()
                    target = msg.get("game", "lobby")
                    room.current_game = target
                    if target == "stop777":
                        room.game_state = {"phase": "ready", "results": {}, "ordered": [], "revealed_count": 0, "awarded": {}}
                    elif target == "bomb":
                        room.game_state = {
                            "phase": "ready",
                            "doc_type": random.choice(["Spot", "BPA"]),
                            "order": list(room.players.keys()),
                            "holder": None,
                            "pass_count": 0,
                            "loser": None,
                            "survivors": [],
                        }
                    elif target == "rhythm":
                        room.game_state = {"phase": "ready", "scores": {}, "duration": 38, "awarded": {}, "ranked": []}
                    elif target == "quiz":
                        room.game_state = {"phase": "ready", "index": 0, "choices": {}, "winners": []}
                    else:
                        room.game_state = {}
                    await room.broadcast()

                # --- GAME 1: 7.77s ---
                elif mtype == "stop777_start":
                    room.cancel_tasks()
                    start_ts = time.time() + 3.0  # 3 sec countdown
                    room.game_state = {
                        "phase": "running",
                        "start_ts": start_ts,
                        "server_now": time.time(),
                        "results": {},
                        "ordered": [],
                        "revealed_count": 0,
                        "awarded": {},
                    }
                    await room.broadcast()
                    t = asyncio.create_task(run_bot_stop777(room, start_ts))
                    room.bg_tasks.append(t)

                elif mtype == "stop777_finish":
                    room.cancel_tasks()
                    results = room.game_state.get("results", {})
                    # Add players who didn't stop as DNF (diff = 99.99)
                    ordered = []
                    for pid in room.players.keys():
                        if pid in results:
                            ordered.append({
                                "id": pid,
                                "time": results[pid]["time"],
                                "diff": results[pid]["diff"],
                                "dnf": False,
                            })
                        else:
                            ordered.append({
                                "id": pid,
                                "time": None,
                                "diff": 99.99,
                                "dnf": True,
                            })
                    # Sort from WORST (largest diff) to BEST (smallest diff) so reveal goes last -> 1st!
                    ordered.sort(key=lambda x: (-x["diff"], x["id"]))
                    # Award points based on best rank (reverse of ordered)
                    best_first = list(reversed(ordered))
                    awards = [120, 90, 70, 50, 35]
                    awarded = {}
                    for idx, item in enumerate(best_first):
                        if item["dnf"]:
                            pts = 0
                        else:
                            pts = awards[idx] if idx < len(awards) else 20
                        room.players[item["id"]]["score"] += pts
                        awarded[item["id"]] = pts
                        item["rank"] = idx + 1
                        item["pts"] = pts

                    room.game_state["phase"] = "reveal"
                    room.game_state["ordered"] = ordered
                    room.game_state["revealed_count"] = 0
                    room.game_state["awarded"] = awarded
                    await room.broadcast()

                elif mtype == "stop777_reveal_next":
                    if room.game_state.get("phase") == "reveal":
                        total = len(room.game_state.get("ordered", []))
                        cur = room.game_state.get("revealed_count", 0)
                        if cur < total:
                            room.game_state["revealed_count"] = cur + 1
                            await room.broadcast()

                elif mtype == "stop777_reveal_all":
                    if room.game_state.get("phase") == "reveal":
                        room.game_state["revealed_count"] = len(room.game_state.get("ordered", []))
                        await room.broadcast()

                # --- GAME 2: BOMB (Spot / BPA) ---
                elif mtype == "bomb_start":
                    room.cancel_tasks()
                    pids = list(room.players.keys())
                    if len(pids) < 2:
                        await ws.send_text(json.dumps({"type": "toast", "message": "최소 2명 이상 참여해야 시작할 수 있습니다! (AI 봇을 추가해보세요)"}, ensure_ascii=False))
                        continue
                    random.shuffle(pids)
                    doc_type = msg.get("doc_type") or random.choice(["Spot", "BPA"])
                    duration = random.uniform(13.0, 24.0)
                    room.game_state = {
                        "phase": "running",
                        "doc_type": doc_type,
                        "order": pids,
                        "holder": random.choice(pids),
                        "pass_count": 0,
                        "start_ts": time.time(),
                        "last_pass_ts": time.time(),
                        "loser": None,
                        "survivors": [],
                    }
                    await room.broadcast()
                    t = asyncio.create_task(run_bomb_loop(room, duration))
                    room.bg_tasks.append(t)

                # --- GAME 3: RHYTHM ---
                elif mtype == "rhythm_start":
                    room.cancel_tasks()
                    start_ts = time.time() + 3.0
                    bot_skills = {
                        pid: random.uniform(0.75, 1.35)
                        for pid, p in room.players.items()
                        if p.get("is_bot")
                    }
                    room.game_state = {
                        "phase": "running",
                        "start_ts": start_ts,
                        "server_now": time.time(),
                        "duration": 38,
                        "scores": {pid: {"score": 0, "combo": 0, "perfect": 0} for pid in room.players.keys()},
                        "bot_skills": bot_skills,
                        "awarded": {},
                        "ranked": [],
                    }
                    await room.broadcast()
                    t = asyncio.create_task(run_rhythm_loop(room, 41.0))
                    room.bg_tasks.append(t)

                elif mtype == "rhythm_stop":
                    room.cancel_tasks()
                    if room.game_state.get("phase") == "running":
                        await finish_rhythm(room)

                # --- GAME 4: QUIZ ---
                elif mtype == "quiz_open":
                    room.cancel_tasks()
                    idx = msg.get("index", room.game_state.get("index", 0))
                    if idx < 0 or idx >= len(room.quizzes):
                        idx = 0
                    room.game_state = {
                        "phase": "open",
                        "index": idx,
                        "choices": {},
                        "winners": [],
                    }
                    await room.broadcast()
                    t = asyncio.create_task(run_bot_quiz(room))
                    room.bg_tasks.append(t)

                elif mtype == "quiz_lock":
                    room.cancel_tasks()
                    if room.game_state.get("phase") == "open":
                        room.game_state["phase"] = "locked"
                        await room.broadcast()

                elif mtype == "quiz_reveal":
                    room.cancel_tasks()
                    if room.game_state.get("phase") in ("open", "locked"):
                        idx = room.game_state.get("index", 0)
                        ans = room.quizzes[idx]["a"]
                        winners = []
                        for pid, ch in room.game_state.get("choices", {}).items():
                            if ch == ans and pid in room.players:
                                room.players[pid]["score"] += 50
                                winners.append(pid)
                        room.game_state["phase"] = "revealed"
                        room.game_state["winners"] = winners
                        await room.broadcast()

                elif mtype == "quiz_add":
                    q_text = (msg.get("q") or "").strip()
                    a_val = msg.get("a", "O")
                    exp = (msg.get("exp") or f"정답은 {a_val} 입니다!").strip()
                    if q_text and a_val in ("O", "X"):
                        room.quizzes.append({"q": q_text, "a": a_val, "exp": exp})
                        await room.broadcast()

            # --- PLAYER ACTIONS ---
            elif role == "player" and player_id:
                if mtype == "stop777_press":
                    if room.current_game == "stop777" and room.game_state.get("phase") == "running":
                        if player_id not in room.game_state["results"]:
                            elapsed = msg.get("elapsed")
                            if elapsed is None:
                                elapsed = max(0.0, time.time() - room.game_state["start_ts"])
                            elapsed = round(float(elapsed), 2)
                            room.game_state["results"][player_id] = {
                                "time": elapsed,
                                "diff": round(abs(elapsed - 7.77), 2),
                            }
                            await room.broadcast()

                elif mtype == "bomb_pass":
                    if room.current_game == "bomb" and room.game_state.get("phase") == "running":
                        if room.game_state.get("holder") == player_id:
                            now = time.time()
                            if now - room.game_state.get("last_pass_ts", 0) < 0.25:
                                continue
                            target = msg.get("target")
                            order = room.game_state.get("order", [])
                            others = [pid for pid in order if pid != player_id]
                            if not others:
                                continue
                            if target and target in others:
                                nxt = target
                            else:
                                # Default: next person in circle or random
                                if msg.get("mode") == "next":
                                    idx = order.index(player_id)
                                    nxt = order[(idx + 1) % len(order)]
                                else:
                                    nxt = random.choice(others)
                            room.game_state["holder"] = nxt
                            room.game_state["pass_count"] = room.game_state.get("pass_count", 0) + 1
                            room.game_state["last_pass_ts"] = now
                            await room.broadcast()

                elif mtype == "rhythm_score":
                    if room.current_game == "rhythm" and room.game_state.get("phase") == "running":
                        room.game_state["scores"][player_id] = {
                            "score": int(msg.get("score", 0)),
                            "combo": int(msg.get("combo", 0)),
                            "perfect": int(msg.get("perfect", 0)),
                        }
                        await room.broadcast()

                elif mtype == "quiz_choose":
                    if room.current_game == "quiz" and room.game_state.get("phase") == "open":
                        ch = msg.get("choice")
                        if ch in ("O", "X"):
                            room.game_state["choices"][player_id] = ch
                            await room.broadcast()

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        if room:
            if role == "host" and room.host_ws == ws:
                room.host_ws = None
            elif role == "player" and player_id:
                if room.player_ws.get(player_id) == ws:
                    room.player_ws.pop(player_id, None)
                if player_id in room.players:
                    room.players[player_id]["connected"] = False
                try:
                    await room.broadcast()
                except Exception:
                    pass
