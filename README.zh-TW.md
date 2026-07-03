# Fable Soul

[English](README.md) | 繁體中文

**AI coding agent 的判斷力層（judgment layer）— 讓你的 AI 像資深工程師一樣思考、驗證、溝通。**

大多數 AI agent 的失敗不是知識不足。模型明明會寫那段程式碼，卻在沒跑過任何東西的情況下回報「完成了」、只修表面症狀不修根因、對十秒就能驗證的事說「應該可以」、或是明明能直接做完卻停下來問「要不要我修？」。Fable Soul 是一套從真實失敗中提煉、經過實測的操作規則，直接在行為層面修掉這些毛病——並附上一整套工具，讓規則能隨著你的 agent 持續演化。

支援 **Claude Code** 和 **Codex**（任何會讀 Markdown 指令的 runner 都能用）。

## 內容結構

```
fable-soul/
├── SKILL.md                        # Skill 進入點（三種模式：Embody / Maintain / Transfer）
├── references/
│   ├── soul.md                     # 判斷力規則本體 — 本專案的核心
│   ├── maintenance.md              # Mirror 地圖、同步流程、失敗捕捉迴圈
│   └── transfer-prompts.md         # 6 個把經驗轉成 skill 的 prompt 模板
└── scripts/
    ├── sync_soul.py                # 同步規則到所有安裝位置、偵測 drift
    └── validate_skill.py           # Skill 套件結構驗證
```

## 模組介紹

### 1. 判斷力規則（`references/soul.md`）

19 條操作規則加上可執行的關卡（gates）。重點：

- **Operating Gates** — 任務啟動關卡（目標 / 機制 / 證明）、依任務類型配對驗證方式的 Proof Contract（程式、前端、SEO/發佈、寫作各有各的驗證標準）、以及 Red Flag 的對應恢復動作。
- **先找根因才准修** — 在 agent 能用一句話說清 bug 的機制之前，任何修改都不能出手。
- **先驗證才准說完成** — 「done」需要觀察到的證據；檔案編輯成功只證明 agent 打了字。
- **把工作做完** — 可逆的、範圍內的工作直接做，不要問「要不要我修？」。
- **能量測就不要模糊** — 一分鐘內能驗證的主張就去驗證；數字勝過形容詞。
- **合理化藉口對照表** — 模型會給的原話藉口（「edit 成功了所以完成了」、「測試大概會過」）逐一對應為什麼是錯的。每一列都是從真實失敗中逐字捕捉的。
- **Red Flags 檢查清單** — agent 在結束每一輪回覆前跑的自我檢查。

### 2. 三種操作模式（`SKILL.md`)

- **Embody（體現）** — 把規則載入當前 session，默默照著做，不對使用者朗誦規則。
- **Maintain（維護）** — 把新的失敗捕捉進規則（RED–GREEN 測試迴圈：先在沒有新規則的情況下重現失敗，套上最小修改，確認行為翻轉）、保持各安裝位置同步、定期審計瘦身讓規則檔維持可載入的長度。
- **Transfer（轉移）** — 把更強模型的建議、事後檢討、session 教訓轉成耐用的 skill，保留機制而不是氛圍。

### 3. Transfer prompts（`references/transfer-prompts.md`）

六個可直接使用的 prompt 模板：

| Prompt | 用途 |
|--------|------|
| Departing Principal | 讓強模型把專案判斷力轉成弱模型/便宜模型能用的 skill 庫 |
| Instruction Audit | 在加新規則之前，先找出過時、矛盾、過度規範的舊規則 |
| Failure Archaeology | 挖掘 git 歷史和事後檢討，讓未來的 agent 不用重打已解決的仗 |
| Executable Campaign | 產出有決策關卡的計畫：精確指令、預期輸出、分支點 |
| Fresh Verifier | 獨立驗證輪，在回報「完成」之前抓出沒有證據的主張 |
| Skill Library Review | 三輪審計（事實 / 準則 / 可用性）檢查生成的 skill 庫 |

### 4. 同步與 drift 工具（`scripts/`）

- `sync_soul.py` — 把 skill 複製到 `~/.claude/skills/` 和 `~/.codex/skills/`，並從單一 canonical 來源重新生成全域指令檔（`~/.claude/CLAUDE.md`、`~/.codex/AGENTS.md`）。加 `--check` 只回報 drift、不做任何變更。腳本**不會覆寫**不是它產生的全域檔案——會跳過並警告。
- `validate_skill.py` — 檢查 frontmatter、引用連結、套件結構。

## 安裝

**方式 A — 只裝 skill（非侵入式）。** 把資料夾複製到 skills 目錄：

```bash
# Claude Code
cp -r fable-soul ~/.claude/skills/fable-soul

# Codex
cp -r fable-soul ~/.codex/skills/fable-soul
```

規則會在 skill 被呼叫時載入。

**方式 B — 常駐生效（推薦）。** 在 repo 根目錄執行同步腳本：

```bash
python scripts/sync_soul.py          # 安裝到所有位置 + 生成全域檔案
python scripts/sync_soul.py --check  # 驗證全部同步
```

這會讓規則透過全域指令檔在**每個** session 載入。如果你已經有自己的 `CLAUDE.md` / `AGENTS.md`，腳本會跳過它——請手動把 `references/soul.md` 的本體貼進你現有的檔案。

## 維護你自己的規則

規則的設計是從**你的** agent 的失敗中長出來，不是抄通用建議：

1. 你的 agent 回報了假的「完成」或找了藉口——**逐字**記下那句合理化。
2. 檢查是否已有規則涵蓋。有的話，強化那條規則，不要加重複的新規則。
3. **RED**：在沒有新規則的全新 session 中重現該失敗。
4. **GREEN**：套上最小修改，重跑同一情境，確認行為翻轉。
5. 同步：`python scripts/sync_soul.py`。

沒有測試過的規則修改一律不出貨。另外有成長預算：`soul.md` 超過約 250 行就先瘦身再新增——模型會跳著看的判斷力層，比一個短但會被讀完的更糟。

## 設計原則

- **單一事實來源。** `references/soul.md` 是 canonical；所有安裝位置都是腳本重新生成的 mirror。drift 可偵測、修復是機械化的。
- **規則必須可執行。** 每條規則都要有它預防的失敗模式、觸發條件、改變的行為、和驗證面。「多想一點」這種空話不合格。
- **建議不是基礎設施。** 部落格文章或強模型的 tip，要先通過捕捉迴圈的考驗才能進來。

## License

MIT

---

*Fable Soul 是獨立的開源專案，與任何 AI 廠商皆無關聯。（Not affiliated with any AI vendor.）*
