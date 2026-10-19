"""Write the talk's diagrams as draw.io files (open and edit them in draw.io / app.diagrams.net).

    python diagrams/build_diagrams.py        writes diagrams/src/*.drawio

Every connector is orthogonal with explicit attachment points, so nothing crosses or overlaps.
Palette is the deck's: ink #1A1A1A, muted #5C6670, line #C9CFCD, panel #F3F6F4, mint #E3FCF7, green #00684A,
bright green #00ED64, red #DB3030, navy #001E2B (dark slides).
"""
from pathlib import Path
from xml.sax.saxutils import escape as _escape
def escape(s): return _escape(s, {'"': "&quot;"})

OUT = Path(__file__).resolve().parent / "src"; OUT.mkdir(parents=True, exist_ok=True)
INK, MUTED, LINE, PANEL, MINT, GREEN, BRIGHT, RED, NAVY, WHITE = "#1A1A1A", "#5C6670", "#C9CFCD", "#F3F6F4", "#E3FCF7", "#00684A", "#00ED64", "#DB3030", "#001E2B", "#FFFFFF"
FONT = "fontFamily=Segoe UI;"

class D:
    def __init__(self, name, dark=False):
        self.name, self.dark, self.cells, self.n = name, dark, [], 0
    def _id(self): self.n += 1; return f"c{self.n}"
    def box(self, x, y, w, h, text, fill=PANEL, stroke=LINE, color=None, size=14, bold=False, dashed=False, mono=False, align="center", rounded=True, sw=1.2, valign="middle"):
        color = color or (WHITE if self.dark else INK)
        st = (f"rounded={1 if rounded else 0};whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth={sw};"
              f"fontColor={color};fontSize={size};align={align};verticalAlign={valign};spacingLeft=8;spacingRight=8;"
              + ("fontStyle=1;" if bold else "") + ("dashed=1;dashPattern=6 4;" if dashed else "")
              + ("fontFamily=Consolas;" if mono else FONT) + ("arcSize=12;" if rounded else ""))
        i = self._id(); self.cells.append((i, text, st, x, y, w, h)); return i
    def text(self, x, y, w, h, text, size=13, color=None, bold=False, align="left", italic=False):
        color = color or (MUTED if not self.dark else "#C9CFCD")
        st = (f"text;html=1;strokeColor=none;fillColor=none;align={align};verticalAlign=middle;whiteSpace=wrap;fontColor={color};fontSize={size};"
              + ("fontStyle=1;" if bold else "") + ("fontStyle=2;" if italic else "") + FONT)
        i = self._id(); self.cells.append((i, text, st, x, y, w, h)); return i
    def edge(self, a, b, exit=(1, 0.5), entry=(0, 0.5), points=None, label=None, color=None, dashed=False, arrow=True, width=1.6):
        color = color or (MUTED if not self.dark else "#8A949A")
        st = (f"edgeStyle=orthogonalEdgeStyle;rounded=1;arcSize=10;html=1;strokeColor={color};strokeWidth={width};"
              f"exitX={exit[0]};exitY={exit[1]};entryX={entry[0]};entryY={entry[1]};exitPerimeter=0;entryPerimeter=0;"
              f"endArrow={'blockThin' if arrow else 'none'};endFill=1;endSize=7;jettySize=auto;"
              + ("dashed=1;dashPattern=6 4;" if dashed else "") + f"fontColor={MUTED};fontSize=12;labelBackgroundColor=#FFFFFF;labelBorderColor=none;spacing=2;" + FONT)
        i = self._id(); self.cells.append(("edge", i, a, b, st, points or [], label)); return i
    def write(self):
        parts = [f'<mxGraphModel grid="0" page="0" background="{NAVY if self.dark else "none"}"><root><mxCell id="0"/><mxCell id="1" parent="0"/>']
        for c in self.cells:
            if c[0] == "edge":
                _, i, a, b, st, pts, label = c
                pts_xml = "".join(f'<mxPoint x="{px}" y="{py}"/>' for px, py in pts)
                lab = f' value="{escape(label)}"' if label else ""
                parts.append(f'<mxCell id="{i}"{lab} style="{st}" edge="1" parent="1" source="{a}" target="{b}"><mxGeometry relative="1" as="geometry">'
                             + (f'<Array as="points">{pts_xml}</Array>' if pts else "") + '</mxGeometry></mxCell>')
            else:
                i, text, st, x, y, w, h = c
                parts.append(f'<mxCell id="{i}" value="{escape(text)}" style="{st}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        parts.append("</root></mxGraphModel>")
        model = "".join(parts)
        xml = f'<mxfile host="build_diagrams.py"><diagram name="{self.name}" id="{self.name}">{model}</diagram></mxfile>'
        (OUT / f"{self.name}.drawio").write_text(xml, encoding="utf-8"); print("wrote", self.name)

# ---- slide 1: the motif -----------------------------------------------------
d = D("s01-motif", dark=True)
a = d.box(0, 0, 96, 44, "LLM", fill="#0B2D3A", stroke="#3B5560", size=13); b = d.box(136, 0, 96, 44, "tool", fill="#0B2D3A", stroke="#3B5560", size=13)
c = d.box(272, 0, 96, 44, "API", fill="#0B2D3A", stroke="#3B5560", size=13); s = d.box(136, 84, 96, 44, "state?", fill="#0B2D3A", stroke=BRIGHT, color=BRIGHT, size=13, bold=True)
d.edge(a, b); d.edge(b, c); d.edge(s, b, exit=(0.5, 0), entry=(0.5, 1), arrow=False, dashed=True, color=BRIGHT); d.write()

# ---- slide 4: the pipeline, with the iteration loop ---------------------------
d = D("s04-pipeline")
names = ["Prompt", "AI agent", "MCP server<br><span style='font-size:11px;color:#5C6670'>tools + skills</span>", "Edge Impulse<br>REST API", "Training job", "Result"]
ids = []
for k, nm in enumerate(names):
    x = k * 196
    ids.append(d.box(x, 0, 156, 58, nm, fill=MINT if k == 2 else PANEL, stroke=GREEN if k == 2 else LINE, bold=(k == 2), sw=1.6 if k == 2 else 1.2))
for k in range(5): d.edge(ids[k], ids[k + 1])
d.edge(ids[5], ids[1], exit=(0.5, 1), entry=(0.5, 1), points=[(5 * 196 + 78, 104), (196 + 78, 104)], label="iterate on DSP and training settings", color=GREEN)
d.write()

# ---- slide 6: state leaking out of the loop ----------------------------------
d = D("s06-leak")
ag = d.box(0, 96, 150, 60, "Agent", fill=MINT, stroke=GREEN, bold=True); tl = d.box(220, 96, 150, 60, "Tools", bold=True)
d.edge(ag, tl); d.edge(tl, ag, exit=(0.5, 1), entry=(0.5, 1), points=[(295, 190), (75, 190)], color=LINE)
chips = ["block IDs", "project / org IDs", "job status", "retries", "previous config", "new result", "approval", "orphaned job"]
chip_ids = []
for k, nm in enumerate(chips):
    col, row = k // 4, k % 4
    x, y = 520 + col * 230, 10 + row * 66
    red = nm == "orphaned job"
    cid = d.box(x, y, 190, 44, nm, fill="#FDEDED" if red else PANEL, stroke=RED if red else LINE, color=RED if red else INK, dashed=not red, size=13)
    if col == 0:
        chip_ids.append(cid); d.edge(tl, cid, exit=(1, 0.5), entry=(0, 0.5), points=[(450, 126), (450, y + 22)], dashed=True, color=LINE, width=1.2)
    else:   # the second column hangs off the first, so no edge crosses a chip
        d.edge(chip_ids[row], cid, exit=(1, 0.5), entry=(0, 0.5), dashed=True, color=RED if red else LINE, width=1.2)
d.text(520, 290, 420, 30, "IDs everywhere · job timing · state management", size=13, color=MUTED)
d.write()

# ---- slide 7: where does this live? ------------------------------------------
d = D("s07-where")
for k, nm in enumerate(["In the prompt?", "In a file?", "In a cache?", "In a database?"]):
    last = k == 3
    d.box(k * 250, 0, 220, 64, nm, fill=MINT if last else PANEL, stroke=GREEN if last else LINE, bold=last, size=16, sw=1.8 if last else 1.2)
d.write()

# ---- slide 11: embed, reference, or log --------------------------------------
d = D("s11-columns")
cols = [("Embed", "small · bounded · read with the parent", ["configuration snapshot", "latest result", "current status"], True),
        ("Reference / split", "large · unbounded · shared", ["job events", "training logs", "artifacts and files"], False),
        ("Append-only log", "the explanation trail", ["actions", "status transitions", "human approvals"], True)]
for k, (title, sub, items, accent) in enumerate(cols):
    x = k * 340
    d.box(x, 0, 300, 330, "", fill=MINT if accent else PANEL, stroke=GREEN if accent else LINE, sw=1.6 if accent else 1.2)
    d.text(x + 16, 12, 268, 30, title, size=18, color=GREEN if accent else INK, bold=True)
    d.text(x + 16, 42, 268, 24, sub, size=12)
    for j, it in enumerate(items): d.box(x + 24, 84 + j * 76, 252, 52, it, fill=WHITE, stroke=LINE, size=14)
d.write()

# ---- slide 12: the question creates the index --------------------------------
d = D("s12-index")
d.text(0, 0, 420, 24, "What the agent asks", size=13); d.text(540, 0, 300, 24, "The index that answers it", size=13)
q1 = d.box(0, 32, 440, 70, 'runs.find({ projectId: "project-512482",<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;status: "training" })', mono=True, size=13, align="left", fill=WHITE)
i1 = d.box(540, 42, 300, 50, "{ projectId: 1, status: 1 }", mono=True, size=13, fill=MINT, stroke=GREEN)
q2 = d.box(0, 134, 440, 70, 'runs.find({ projectId: "project-512482" })<br>&nbsp;&nbsp;&nbsp;&nbsp;.sort({ updatedAt: -1 }).limit(1)', mono=True, size=13, align="left", fill=WHITE)
i2 = d.box(540, 144, 300, 50, "{ projectId: 1, updatedAt: -1 }", mono=True, size=13, fill=MINT, stroke=GREEN)
d.edge(q1, i1, color=GREEN); d.edge(q2, i2, color=GREEN); d.write()

# ---- slide 13: the wait loop --------------------------------------------------
d = D("s13-polling")
ag = d.box(0, 60, 140, 56, "agent", fill=MINT, stroke=GREEN, bold=True)
st = d.box(220, 60, 170, 56, "job status?"); rn = d.box(470, 60, 140, 56, "running"); sl = d.box(690, 60, 150, 56, "sleep…", fill=WHITE, dashed=True)
d.edge(ag, st); d.edge(st, rn); d.edge(rn, sl)
d.edge(sl, st, exit=(0.5, 1), entry=(0.5, 1), points=[(765, 160), (305, 160)], label="× 60", color=RED)
d.text(0, 190, 840, 26, "every check is a read · every wait is latency and tokens · every restart is a place to lose the job ID", size=13)
d.write()

# ---- slide 14: from polling to events (the three steps) ----------------------
d = D("s14-doorbell")
s1 = d.box(0, 0, 330, 78, "<b>1 · Job updates its state</b><br><span style='font-size:12px;color:#5C6670'>updateOne({ runId }, { $set: { status: 'completed' } })</span>", align="left", fill=WHITE)
s2 = d.box(0, 128, 330, 78, "<b>2 · Database emits a change event</b><br><span style='font-size:12px;color:#5C6670'>oplog to change stream, with a resume token</span>", align="left", fill=MINT, stroke=GREEN, sw=1.6)
s3 = d.box(0, 256, 330, 78, "<b>3 · Consumer reacts</b><br><span style='font-size:12px;color:#5C6670'>resume the agent · next tool · ask for approval</span>", align="left", fill=WHITE)
d.edge(s1, s2, exit=(0.5, 1), entry=(0.5, 0), color=GREEN); d.edge(s2, s3, exit=(0.5, 1), entry=(0.5, 0), color=GREEN); d.write()

# ---- slide 15: keep, expire, review -------------------------------------------
d = D("s15-halflife")
cols = [("Keep", ["audit history", "experiment summaries", "approvals", "baseline results"], "keep"),
        ("Expire", ["temporary job state", "session context", "cache", "short-lived tool outputs"], "expire"),
        ("Review", ["raw logs", "failed attempts", "large prompts", "intermediate artifacts"], "review")]
for k, (title, items, kind) in enumerate(cols):
    x = k * 340
    d.text(x, 0, 300, 30, title, size=18, bold=True, color=GREEN if kind == "keep" else (MUTED if kind == "expire" else INK))
    for j, it in enumerate(items):
        if kind == "keep": d.box(x, 40 + j * 62, 300, 48, it, fill=MINT, stroke=GREEN, sw=1.6)
        elif kind == "expire": d.box(x, 40 + j * 62, 300, 48, it, fill="#FAFBFA", stroke=LINE, color="#9AA3A8")
        else: d.box(x, 40 + j * 62, 300, 48, it, fill=WHITE, stroke=MUTED, dashed=True)
d.write()

# ---- slide 17: structured and semantic ---------------------------------------
d = D("s17-semantic")
d.text(0, 0, 430, 24, "A structured question: failed jobs for project X, today.", size=13, italic=True)
d.text(500, 0, 450, 24, "A semantic question: previous failures like this one.", size=13, italic=True, color=GREEN)
a = d.box(0, 30, 430, 110, 'runs.find({<br>&nbsp;&nbsp;projectId: "project-512482",<br>&nbsp;&nbsp;"jobs.status": "failed",<br>&nbsp;&nbsp;updatedAt: { $gte: startOfToday } })', mono=True, size=12, align="left", fill=WHITE)
b = d.box(500, 30, 450, 110, 'runs.aggregate([{ $vectorSearch: {<br>&nbsp;&nbsp;index: "failure_embeddings", path: "failureEmbedding",<br>&nbsp;&nbsp;queryVector: embed(thisFailureSummary),<br>&nbsp;&nbsp;filter: { projectId: "project-512482" }, limit: 5 } }])', mono=True, size=12, align="left", fill=MINT, stroke=GREEN)
c = d.box(325, 220, 300, 56, "one collection · one document", fill=MINT, stroke=GREEN, bold=True)
d.edge(a, c, exit=(0.5, 1), entry=(0, 0.5), points=[(215, 248)], color=MUTED); d.edge(b, c, exit=(0.5, 1), entry=(1, 0.5), points=[(725, 248)], color=GREEN); d.write()

# ---- slide 18: the four guardrails ----------------------------------------------
d = D("s18-guardrails")
ids = []
for k, nm in enumerate(["least privilege", "confirmation gates", "audit trail", "rate limits"]):
    acc = nm == "audit trail"
    ids.append(d.box(k * 300, 0, 250, 56, nm, fill=MINT if acc else PANEL, stroke=GREEN if acc else LINE, bold=acc, sw=1.8 if acc else 1.2, size=15))
for k in range(3): d.edge(ids[k], ids[k + 1], color=GREEN)
d.write()

# ---- slide 19: the resolved architecture ------------------------------------
d = D("s19-resolved")
d.text(0, 0, 200, 24, "What is", size=13); d.text(300, 0, 300, 24, "What could be", size=13, color=GREEN, bold=True)
l1 = d.box(20, 40, 140, 50, "LLM", fill=WHITE, stroke=LINE, color=MUTED, dashed=True); l2 = d.box(20, 140, 140, 50, "tool", fill=WHITE, stroke=LINE, color=MUTED, dashed=True); l3 = d.box(20, 240, 140, 50, "API", fill=WHITE, stroke=LINE, color=MUTED, dashed=True)
d.edge(l1, l2, exit=(0.5, 1), entry=(0.5, 0), color=LINE); d.edge(l2, l3, exit=(0.5, 1), entry=(0.5, 0), color=LINE)
ag = d.box(300, 150, 150, 60, "Agent", fill=MINT, stroke=GREEN, bold=True); tl = d.box(500, 150, 150, 60, "Tools", bold=True)
sl = d.box(720, 30, 70, 300, "State layer", fill=GREEN, stroke=GREEN, color=WHITE, bold=True, size=13)
d.edge(ag, tl); d.edge(tl, sl, color=GREEN)
outs = ["structured queries", "workflow state", "history + audit", "semantic retrieval", "events"]
for k, nm in enumerate(outs):
    o = d.box(860, 37 + k * 60, 200, 46, nm, fill=WHITE, stroke=GREEN, size=13)   # centres line up with the exits at 60 + 60k
    d.edge(sl, o, exit=(1, (k + 0.5) / 5), entry=(0, 0.5), color=GREEN, width=1.3)
ap = d.box(1120, 150, 150, 60, "APIs / jobs", bold=True)
d.edge(sl, ap, exit=(0.5, 1), entry=(0.5, 1), points=[(755, 360), (1195, 360)], color=GREEN, label="only through the state layer")
d.write()

# ---- slide 31: what the server is doing underneath --------------------------
d = D("s31-server")
steps = [("Driver", "the agent's write"), ("Query engine", "plan, use the index"), ("WiredTiger cache", "documents + index pages; dirty pages in orange"),
         ("Journal", "durable before the checkpoint"), ("Checkpoint", "flush to collection files"), ("Oplog", "replication and change streams read here")]
ids = []
for k, (nm, sub) in enumerate(steps):
    x = k * 200
    ids.append(d.box(x, 0, 170, 56, nm, bold=True, size=14, fill=MINT if k == 2 else PANEL, stroke=GREEN if k == 2 else LINE))
    d.text(x - 10, 64, 190, 46, sub, size=11, align="center")
for k in range(5): d.edge(ids[k], ids[k + 1], color=GREEN)
d.write()
