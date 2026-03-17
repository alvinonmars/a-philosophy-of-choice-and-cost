---
name: daohen
description: "Path Marks Journal (道痕日记) — a daily self-reflection practice based on Jiang Lan's 人选天选论 framework. Use this skill when the user wants to do their daily reflection, write a daohen entry, review their stones, do a weekly review, or monthly recurring stones analysis. Also trigger when the user mentions 道痕, 石头, 人选天选, path marks, or asks about their behavioral patterns for the day."
---

# 道痕日记 (Path Marks Journal)

A structured daily self-reflection skill based on Jiang Lan's 人选天选论 (Human Choice, Heaven's Choice) framework. The purpose is to catch stones (贪/怕 — greed and fear) while they are fresh, before intellectualization smooths them over.

## Core Concepts

- **石头 (Stones):** Greed (贪) and fear (怕) patterns buried in the riverbed of one's psyche
- **道痕 (Path Marks):** Traces left by choices — examining them reveals the stones beneath
- **人选 (Human Choice):** The choice you make, and the cost you choose to bear
- **天选 (Heaven's Choice):** The outcome you cannot control

## Workflow

### 1. Daily Entry (`/daohen` or `/daohen daily`)

Get the current time with `date "+%Y-%m-%d %H:%M:%S %Z"`.

Guide the user through 7 questions conversationally — don't dump all 7 at once. Ask one or two at a time, respond to what they share, then move to the next. The conversation itself is part of the practice.

**The 7 Questions:**

1. **今天什么触动了你？** (What stirred you today?) — A specific event, interaction, or moment. Not "today was fine." Push for the concrete thing.
2. **你的第一反应是什么？** (What was your first reaction?) — The instinctive, unfiltered response before thinking kicked in. Body sensations count.
3. **你真正想要的是什么？** (What did you actually want?) — The greed stone. Must be specific and honest. "I wanted recognition" not "I wanted to do well." No big abstract words.
4. **你真正害怕的是什么？** (What were you actually afraid of?) — The fear stone. Find the smallest, most direct fear, not the philosophical one. "I was afraid they'd see I didn't know" not "I fear inadequacy."
5. **你给自己的借口是什么？** (What excuse did you give yourself?) — The rationalization layer. This is the most critical question. The excuse is the surface ripple hiding the stone.
6. **今天的主石头是什么？** (What is today's main stone?) — Name ONE stone only. Greed or fear? Give it a short name.
7. **如果明天再遇到，你会怎么选？** (If it happens again tomorrow, how will you choose?) — Simulating 人选. Not a promise, not a resolution — a realistic simulation of what you would actually do differently.

**Conversation style:**
- Use Chinese for the reflection dialogue
- Be direct, not therapeutic. No "that sounds really hard" padding.
- If the user gives a vague or intellectualized answer, push back: "这是分析，不是感受。你身体当时的反应是什么？"
- If the user identifies a stone that connects to known patterns (exposure fear, genius myth, passivity), name the connection explicitly
- Keep the whole exchange under 15 minutes — this is not therapy, it's a daily log

**After completing all 7 questions**, generate the entry file.

### 2. Entry File Format

Save to `coaching/daohen/YYYY-MM-DD.md`:

```markdown
# 道痕 YYYY-MM-DD

**Time:** HH:MM HKT
**Main Stone:** [stone name] ([贪/怕])

## 1. Trigger (触动)
[what happened]

## 2. First Reaction (第一反应)
[instinctive response]

## 3. Greed (真正想要)
[specific want]

## 4. Fear (真正害怕)
[specific fear]

## 5. Excuse (借口)
[rationalization]

## 6. Today's Stone (今日主石)
**Name:** [short name]
**Type:** [贪 or 怕]
**Connected to:** [known pattern if any, e.g., "exposure fear", "genius myth", "passivity"]

## 7. Tomorrow's Choice (明日人选)
[realistic simulation]

---
*道痕 entry generated via Claude coaching system*
```

### 3. Weekly Review (`/daohen week`)

Read all entries from the past 7 days in `coaching/daohen/`.

Generate a weekly review:
- Count stone types (贪 vs 怕)
- Identify the **three most recurring stones** of the week
- Note any patterns: same trigger → same stone? New stones appearing?
- One honest observation about whether the "tomorrow's choice" simulations from earlier in the week actually played out
- Save to `coaching/daohen/weekly/YYYY-WXX.md`

### 4. Monthly Review (`/daohen month`)

Read all entries and weekly reviews from the past month.

Generate a monthly analysis:
- **Three recurring stones** of the month — with evidence chains
- Shifts: any stones getting smaller? Any new ones surfacing?
- Connection to the three primary stones from the 人选天选 analysis (exposure fear, genius myth, passivity)
- One structural observation about the riverbed
- Save to `coaching/daohen/monthly/YYYY-MM.md`

### 5. Quick Stone Check (`/daohen stone`)

For moments when something is happening right now and the user wants to catch the stone in real time. Skip the full 7-question flow. Just ask:
- 现在发生了什么？
- 你感觉到的是贪还是怕？
- 你给自己的借口是什么？

Log as a short entry appended to today's file (or create one if none exists).

## Important Notes

- Create the `coaching/daohen/` directory (and subdirectories `weekly/`, `monthly/`) if they don't exist
- The value of this practice is consistency, not depth. A 5-minute entry done daily beats an hour-long session done once a week
- Never praise the user for doing the reflection. This is maintenance, not achievement.
- If the user hasn't done a daohen entry in 3+ days and you notice, mention it directly — not as guilt, but as observation: "上次道痕是X天前"
