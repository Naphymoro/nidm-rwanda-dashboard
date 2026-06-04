from __future__ import annotations

import csv
import json
import textwrap
from collections import Counter
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "stress_test_corpus"

REPORT_DOCX = OUT / "climatetales_ndim_desk_review_report.docx"
REPORT_PDF = OUT / "climatetales_ndim_desk_review_report.pdf"
MASTER_CSV = OUT / "climatetales_ndim_synthetic_narratives_master.csv"
MANIFEST = OUT / "climatetales_ndim_corpus_manifest.json"
BONUS_TXT = OUT / "climatetales_bonus_manual_story.txt"

ROUTE_FILES = {
    "structured_interview": OUT / "climatetales_structured_interview_synthetic.csv",
    "open_story": OUT / "climatetales_open_story_synthetic.csv",
    "indigenous_knowledge": OUT / "climatetales_indigenous_knowledge_synthetic.csv",
    "citizen_science": OUT / "climatetales_citizen_science_synthetic.csv",
    "crowd_batch": OUT / "climatetales_crowdsourced_batch_synthetic.csv",
    "experimental_feed": OUT / "climatetales_social_media_feeds_synthetic.csv",
}

HEADERS = [
    "narrative_id",
    "evidence_mode",
    "interview_id",
    "country",
    "province",
    "district",
    "sector",
    "cell",
    "village",
    "respondent_profile",
    "respondent_role",
    "household_cooking_role",
    "primary_decision_maker",
    "current_cooking_methods",
    "adoption_status",
    "technology_focus",
    "intervention_channel",
    "source_type",
    "source_name",
    "period",
    "language",
    "consent_tier",
    "visibility",
    "reviewer",
    "observation_date",
    "location_precision",
    "validation_status",
    "community_validation",
    "knowledge_type",
    "knowledge_holder",
    "sensitivity",
    "attribution",
    "contributor_type",
    "citizen_confidence",
    "feed_sources",
    "platform",
    "source_actor",
    "trusted_messenger",
    "perceived_harm_fear",
    "indigenous_knowledge_status",
    "q1",
    "q2",
    "q3",
    "q4",
    "q5",
    "narrative",
    "tone_archetype",
    "adoption_stance",
    "key_barrier",
    "key_motivator",
    "social_influence",
    "translation_notes",
    "benefit_sharing",
    "manual_barrier_strength",
    "trust_signal",
    "misinformation_risk",
    "inoculation_opportunity",
    "emotional_intensity",
    "credibility_local_grounding",
    "expected_ndim_signal",
]

BASE_YEAR = "2026"

LOCATIONS = [
    ("Kigali City", "Gasabo", "Kimironko", "Bibare", "Umucyo"),
    ("Kigali City", "Kicukiro", "Gahanga", "Karembure", "Amahoro"),
    ("Kigali City", "Nyarugenge", "Nyamirambo", "Rwezamenyo", "Agatare"),
    ("Northern Province", "Musanze", "Muhoza", "Cyabararika", "Kabeza"),
    ("Northern Province", "Musanze", "Kinigi", "Kaguhu", "Bisoke"),
    ("Eastern Province", "Nyagatare", "Rwimiyaga", "Kirebe", "Rugarama"),
    ("Eastern Province", "Rwamagana", "Kigabiro", "Cyanya", "Nyagasenyi"),
    ("Western Province", "Rubavu", "Gisenyi", "Mbugangari", "Byahi"),
    ("Western Province", "Rusizi", "Kamembe", "Cyangugu", "Gihundwe"),
    ("Southern Province", "Huye", "Tumba", "Cyimana", "Rango"),
    ("Southern Province", "Nyamagabe", "Kamegeri", "Bwama", "Kigarama"),
    ("Southern Province", "Nyaruguru", "Busanze", "Raranzige", "Mubuga"),
]

PROFILES = [
    ("24-34, female, market vendor", "primary cook", "daily cooking lead", "yes"),
    ("35-44, male, motorcycle taxi rider", "budget contributor", "fuel purchaser", "no"),
    ("45-54, female, farmer and savings-group member", "primary cook", "daily cooking lead", "yes"),
    ("55-64, female, elder caregiver", "elder adviser", "cooking adviser", "yes"),
    ("18-24, male, youth volunteer", "student/youth catalyst", "occasional cook", "no"),
    ("30-39, female, community health worker", "trusted messenger", "household cook", "yes"),
    ("40-49, male, local cooperative leader", "community mobilizer", "fuel decision partner", "yes"),
    ("25-34, female, teacher", "school communicator", "family cook", "yes"),
    ("35-44, female, small restaurant owner", "commercial cook", "business energy manager", "yes"),
    ("50-59, male, repair technician", "technical adviser", "maintenance supporter", "no"),
]

TECH = [
    ("electric pressure cooker", "demonstration kitchen and savings group"),
    ("improved biomass cookstove", "community health worker visit"),
    ("pellet stove", "pay-as-you-cook retailer"),
    ("LPG stove", "urban fuel-switching campaign"),
    ("briquette stove", "cooperative briquette supply"),
    ("school demonstration kitchen", "teacher-led peer learning"),
    ("biogas digester", "livestock cooperative demonstration"),
    ("repair and maintenance support", "after-sales service desk"),
    ("community radio SBCC", "radio drama and call-in programme"),
    ("waste-to-energy cooking fuel", "youth climate innovation group"),
]

ROUTE_INFO = {
    "structured_interview": ("interview", "enumerator_q1_q5", "Structured Interview"),
    "open_story": ("field_note", "open_story_collection", "Open Story"),
    "indigenous_knowledge": ("indigenous_knowledge", "community_knowledge_circle", "Indigenous Knowledge"),
    "citizen_science": ("citizen_report", "citizen_science_observation", "Citizen Science Report"),
    "crowd_batch": ("csv", "crowdsourced_submission_batch", "Crowdsourced Batch"),
    "experimental_feed": ("social_feed", "digital_listening_feed", "Social Media Feeds"),
}

SOURCE_ACTORS = [
    "neighbour",
    "mother-in-law",
    "sector health worker",
    "youth climate catalyst",
    "church savings group",
    "stove vendor",
    "radio caller",
    "WhatsApp group member",
    "school parent committee",
    "market association leader",
]

MESSENGERS = [
    "community health worker",
    "savings-group chair",
    "respected elder cook",
    "school cook",
    "local technician",
    "women cooperative leader",
    "church leader",
    "trained youth catalyst",
    "sector social affairs officer",
    "neighbour who already uses the stove",
]

TONE = [
    "pragmatic",
    "anxious",
    "hopeful",
    "skeptical",
    "protective",
    "aspirational",
    "frustrated",
    "curious",
    "cautious",
    "confident",
]

STANCE = [
    "mixed",
    "against",
    "for",
    "mixed",
    "mixed",
    "for",
    "against",
    "mixed",
    "for",
    "mixed",
]

BARRIERS = [
    "upfront cost",
    "safety fear",
    "taste and food texture",
    "repair access",
    "electricity reliability",
    "fuel availability",
    "gendered workload",
    "trust in vendor",
    "habit and cooking identity",
    "misinformation",
]

MOTIVATORS = [
    "time savings",
    "reduced smoke",
    "fuel savings",
    "clean kitchen",
    "child health",
    "status and modernity",
    "forest protection",
    "less firewood collection",
    "school attendance for children",
    "business productivity",
]


def score_tuple(index: int, route: str) -> tuple[float, float, float, float, float, float, str]:
    """Create deliberately varied, plausible scores for stress-testing encoders."""
    barrier = [0.25, 0.78, 0.44, 0.61, 0.38, 0.72, 0.55, 0.32, 0.69, 0.48][index % 10]
    trust = [0.82, 0.31, 0.66, 0.44, 0.77, 0.53, 0.28, 0.71, 0.58, 0.63][index % 10]
    misinfo = [0.12, 0.74, 0.22, 0.43, 0.31, 0.18, 0.68, 0.27, 0.51, 0.36][index % 10]
    inoc = min(0.95, (misinfo * 0.58) + (barrier * 0.31) + (1 - trust) * 0.22)
    emotion = [0.42, 0.84, 0.53, 0.67, 0.48, 0.58, 0.77, 0.39, 0.72, 0.61][index % 10]
    grounding = [0.88, 0.71, 0.92, 0.79, 0.83, 0.86, 0.68, 0.91, 0.74, 0.80][index % 10]
    if route == "indigenous_knowledge":
        grounding = min(0.96, grounding + 0.06)
        emotion = min(0.93, emotion + 0.04)
    if route == "experimental_feed":
        grounding = max(0.52, grounding - 0.13)
        misinfo = min(0.88, misinfo + 0.09)
        inoc = min(0.95, inoc + 0.08)
    if route == "citizen_science":
        trust = min(0.9, trust + 0.05)
    if barrier >= 0.65 and misinfo >= 0.5:
        signal = "high inoculation need; test prebunk and trusted messenger strategy"
    elif trust >= 0.7 and barrier <= 0.45:
        signal = "adoption acceleration opportunity; amplify trusted peer proof"
    elif route == "indigenous_knowledge":
        signal = "requires community validation before policy use"
    else:
        signal = "mixed pathway; model sensitivity to trust and cost parameters"
    return barrier, trust, misinfo, inoc, emotion, grounding, signal


def clean(text: str) -> str:
    return " ".join(textwrap.dedent(text).strip().split())


def narrative_body(index: int, route: str, loc: tuple[str, str, str, str, str], profile: tuple[str, str, str, str], tech: tuple[str, str]) -> str:
    province, district, sector, cell, village = loc
    profile_text, role, household_role, decision = profile
    technology, channel = tech
    actor = SOURCE_ACTORS[index % len(SOURCE_ACTORS)]
    messenger = MESSENGERS[index % len(MESSENGERS)]
    barrier = BARRIERS[index % len(BARRIERS)]
    motivator = MOTIVATORS[index % len(MOTIVATORS)]
    opening = {
        "structured_interview": "During the interview",
        "open_story": "In a long field note",
        "indigenous_knowledge": "In a community knowledge circle",
        "citizen_science": "In a citizen science observation",
        "crowd_batch": "In a crowdsourced submission",
        "experimental_feed": "In a social media listening extract",
    }[route]
    if route == "experimental_feed":
        return clean(
            f"""
            {opening} from {district}, several posts and voice-note summaries discussed {technology}.
            One {actor} said the device is useful but repeated that it might spoil beans or increase the monthly bill.
            Another household in {sector} answered that the last demonstration showed faster cooking and less smoke.
            The thread shows a mixed signal: people want {motivator}, but the story of {barrier} spreads faster than the official explanation.
            A locally trusted response from a {messenger} would likely be more persuasive than a national slogan.
            """
        )
    if route == "indigenous_knowledge":
        return clean(
            f"""
            {opening} in {village}, elders compared {technology} with older practices for cooking beans during rainy seasons.
            They explained that smoke has long been treated as part of kitchen life, but also said children coughing at night is not normal.
            The concern was not rejection of clean cooking; it was whether the new system respects food texture, family timing, and neighbourly proof.
            The group suggested that any intervention should be demonstrated by a {messenger} and explained through local examples, not only price tables.
            This knowledge should be returned to the community before being used as a policy claim.
            """
        )
    if route == "citizen_science":
        return clean(
            f"""
            {opening} from {cell}, the contributor recorded three cooking sessions before and after trying {technology}.
            Smoke was lower on days when the stove was used correctly, but the family reverted to the old method when fuel supply was delayed.
            The contributor notes {barrier} as the main obstacle and {motivator} as the main reason to continue testing.
            The observation is useful because it records time, place, confidence, and repeated household behaviour rather than a single opinion.
            """
        )
    if route == "crowd_batch":
        return clean(
            f"""
            {opening} from {district}, a {profile_text} described hearing about {technology} through {channel}.
            The household was not opposed, but the decision was slowed by {barrier}, especially after a {actor} shared a doubtful story.
            The same account also says {motivator} matters because cooking time competes with work, school preparation, and market travel.
            The story should be reviewed for duplication and consent, then encoded as one record in the batch queue.
            """
        )
    if route == "open_story":
        return clean(
            f"""
            {opening} from {sector}, a {profile_text} described cooking beans, cassava leaves, and tea while moving between childcare and income work.
            The person had seen {technology} during {channel}, but trust depended on whether a neighbour could show the same meal cooked well.
            The story turns on {barrier}: the technology sounds promising, yet the household fears wasting money or food if it fails.
            The positive opening is {motivator}, because a cleaner and faster kitchen would change the rhythm of the day.
            """
        )
    return clean(
        f"""
        {opening}, a {profile_text} in {sector} described the household's decision around {technology}.
        The respondent saw value in {motivator} but hesitated because of {barrier}.
        The narrative shows that adoption is not a simple yes or no; it depends on trusted proof, money timing, after-sales service, and whether the meal still feels familiar.
        """
    )


def q_responses(index: int, loc: tuple[str, str, str, str, str], profile: tuple[str, str, str, str], tech: tuple[str, str]) -> tuple[str, str, str, str, str]:
    province, district, sector, cell, village = loc
    profile_text, role, household_role, decision = profile
    technology, channel = tech
    barrier = BARRIERS[index % len(BARRIERS)]
    motivator = MOTIVATORS[index % len(MOTIVATORS)]
    actor = SOURCE_ACTORS[index % len(SOURCE_ACTORS)]
    return (
        clean(
            f"I started the main meal after fetching water in {village}. Beans were already soaked, but I still needed to keep the fire strong and check smoke while children prepared for school."
        ),
        clean(
            f"I first heard about the {technology} through {channel}. My first thought was that it could save time, but I wanted proof that it works for our normal food."
        ),
        clean(
            f"People around me are divided. One {actor} says it is modern and clean; another says the food may not taste the same or that repairs will be difficult."
        ),
        clean(
            f"The decision is difficult because {barrier} matters for our household budget and daily routine. If the first trial fails, people will say we wasted money."
        ),
        clean(
            f"If the technology works, {motivator} would be the biggest change. I would still keep another stove for backup until I fully trust the new system."
        ),
    )


def make_record(route: str, i: int) -> dict[str, str]:
    loc = LOCATIONS[(i + len(route)) % len(LOCATIONS)]
    profile = PROFILES[i % len(PROFILES)]
    tech = TECH[(i + len(route)) % len(TECH)]
    province, district, sector, cell, village = loc
    source_type, source_name, route_label = ROUTE_INFO[route]
    barrier, trust, misinfo, inoc, emotion, grounding, signal = score_tuple(i, route)
    q1, q2, q3, q4, q5 = q_responses(i, loc, profile, tech) if route == "structured_interview" else ("", "", "", "", "")
    narrative = "" if route == "structured_interview" else narrative_body(i, route, loc, profile, tech)
    source_actor = SOURCE_ACTORS[i % len(SOURCE_ACTORS)]
    messenger = MESSENGERS[i % len(MESSENGERS)]
    platform = ["WhatsApp", "community radio", "Facebook", "X/Twitter", "LinkedIn", "local meeting notes"][i % 6]
    feed_sources = ""
    if route == "experimental_feed":
        feed_sources = ";".join(["WhatsApp", "community radio", "Facebook"] if i % 2 else ["X/Twitter", "LinkedIn", "WhatsApp"])
    if route == "crowd_batch":
        feed_sources = "community form;SMS summary;field enumerator upload"
    if route == "citizen_science":
        feed_sources = "household observation sheet;photo log"
    knowledge_type = {
        "indigenous_knowledge": "seasonal cooking memory" if i % 2 else "elder testimony",
        "citizen_science": "household observation",
        "experimental_feed": "digital listening",
    }.get(route, "")
    sensitivity = "sensitive" if route == "indigenous_knowledge" and i % 3 == 0 else "ordinary"
    validation = "pending community validation" if route in {"indigenous_knowledge", "experimental_feed", "crowd_batch"} else "field reviewed"
    return {
        "narrative_id": f"CT-RW-{route.replace('_', '-').upper()}-{i + 1:02d}",
        "evidence_mode": route,
        "interview_id": f"RW-{district[:3].upper()}-{route[:3].upper()}-{i + 1:03d}",
        "country": "Rwanda",
        "province": province,
        "district": district,
        "sector": sector,
        "cell": cell,
        "village": village,
        "respondent_profile": profile[0],
        "respondent_role": profile[1],
        "household_cooking_role": profile[2],
        "primary_decision_maker": profile[3],
        "current_cooking_methods": ["firewood; charcoal", "charcoal; LPG", "firewood; improved stove", "LPG; charcoal backup", "three-stone fire; improved stove"][i % 5],
        "adoption_status": ["aware but not adopted", "trial user", "regular user with backup", "former user", "interested non-user"][i % 5],
        "technology_focus": tech[0],
        "intervention_channel": tech[1],
        "source_type": source_type,
        "source_name": source_name,
        "period": BASE_YEAR,
        "language": "English",
        "consent_tier": ["research_use", "policy_summary_only", "restricted", "research_use"][i % 4],
        "visibility": ["project_team", "workspace_only", "approved_repository", "project_team"][i % 4],
        "reviewer": "synthetic-corpus-generator",
        "observation_date": f"2026-0{(i % 6) + 1}-{10 + i:02d}",
        "location_precision": "sector",
        "validation_status": validation,
        "community_validation": "pending" if route in {"indigenous_knowledge", "crowd_batch", "experimental_feed"} else "reviewed",
        "knowledge_type": knowledge_type,
        "knowledge_holder": "elder women cooking circle" if route == "indigenous_knowledge" else "",
        "sensitivity": sensitivity,
        "attribution": "anonymous",
        "contributor_type": ["enumerator", "community member", "youth catalyst", "field researcher"][i % 4],
        "citizen_confidence": ["medium", "high", "medium", "low"][i % 4] if route == "citizen_science" else "",
        "feed_sources": feed_sources,
        "platform": platform if route == "experimental_feed" else "",
        "source_actor": source_actor,
        "trusted_messenger": messenger,
        "perceived_harm_fear": ["burns", "high bill", "food taste loss", "repair failure", "smoke cough"][i % 5],
        "indigenous_knowledge_status": "requires community return" if route == "indigenous_knowledge" else "",
        "q1": q1,
        "q2": q2,
        "q3": q3,
        "q4": q4,
        "q5": q5,
        "narrative": narrative,
        "tone_archetype": TONE[i % len(TONE)],
        "adoption_stance": STANCE[i % len(STANCE)],
        "key_barrier": BARRIERS[i % len(BARRIERS)],
        "key_motivator": MOTIVATORS[i % len(MOTIVATORS)],
        "social_influence": ["high", "medium", "low", "high", "medium"][i % 5],
        "translation_notes": "Synthetic English rendering; retain Kinyarwanda terms during real transcription.",
        "benefit_sharing": "Return aggregate insights through community meeting before external use.",
        "manual_barrier_strength": f"{barrier:.2f}",
        "trust_signal": f"{trust:.2f}",
        "misinformation_risk": f"{misinfo:.2f}",
        "inoculation_opportunity": f"{inoc:.2f}",
        "emotional_intensity": f"{emotion:.2f}",
        "credibility_local_grounding": f"{grounding:.2f}",
        "expected_ndim_signal": signal,
    }


def make_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for route in ROUTE_FILES:
        for i in range(10):
            rows.append(make_record(route, i))
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=HEADERS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_bonus_story() -> None:
    text = """ClimateTales Rwanda bonus manual story

Evidence route: open_story
Country: Rwanda
Province: Southern Province
District: Nyamagabe
Sector: Kamegeri
Source type: field_note
Source name: synthetic-manual-story
Period: 2026
Consent: research_use
Visibility: project_team

In Kamegeri, a savings-group member explained that clean cooking is not rejected because people dislike technology. The problem is that a family meal is a test of care. If beans are hard, if cassava leaves taste wrong, or if a child says the food smells different, the new device is blamed even when the real issue is training or power timing.

She had seen an electric pressure cooker at a demonstration and liked that it reduced smoke and freed time for evening work. But her neighbour warned that electricity could become expensive and that repairs would be impossible after the project staff left. The respondent said she would trust the change if a local woman who cooks the same food demonstrated it twice, if a technician explained what breaks and what does not, and if the savings group could test one device before asking each household to buy.

This story should produce a mixed adoption stance, moderate-to-high barrier strength, moderate trust, clear inoculation opportunity, and strong local grounding. It is designed for manual stress testing, not as real field evidence.
"""
    BONUS_TXT.write_text(text, encoding="utf-8")


def write_readme(rows: list[dict[str, str]]) -> None:
    counts = Counter(row["evidence_mode"] for row in rows)
    lines = [
        "# ClimateTales Rwanda NDIM stress-test corpus",
        "",
        "This folder contains synthetic, project-grounded narratives for testing NDIM Engine intake, SDMX-style governance, approval, encoding, modelling, inoculation, and policy-output workflows.",
        "",
        "The records are fictional. They are designed to be realistic enough for software and workflow stress testing, but they must not be treated as field evidence.",
        "",
        "## Files",
        "",
        f"- `{MASTER_CSV.name}`: combined import file with {len(rows)} rows.",
    ]
    for route, path in ROUTE_FILES.items():
        lines.append(f"- `{path.name}`: {counts[route]} rows for `{route}`.")
    lines += [
        f"- `{BONUS_TXT.name}`: one single-story text file for manual open-story testing.",
        f"- `{REPORT_DOCX.name}` and `{REPORT_PDF.name}`: desk-review report with citations and professional scientific framing.",
        "",
        "## How to import",
        "",
        "1. Open NDIM Engine.",
        "2. Choose the matching evidence route.",
        "3. Use `Open text or CSV file` in Stage 1.",
        "4. Pick one CSV from this folder, or use the bonus TXT file for a single manual story.",
        "5. Review the SDMX readiness panel, stage the records, approve or reject, and commit reviewed records.",
        "",
        "## SDMX coherence",
        "",
        "All CSVs share common columns for country, administrative unit, source, period, language, consent, visibility, evidence route, narrative text, and route-specific metadata. This lets the tool write different evidence routes into one governed NarrativeRecord ledger.",
        "",
    ]
    (OUT / "README.md").write_text("\n".join(lines), encoding="utf-8")


def write_manifest(rows: list[dict[str, str]]) -> None:
    manifest = {
        "title": "ClimateTales Rwanda NDIM synthetic stress-test corpus",
        "created": date.today().isoformat(),
        "record_count": len(rows),
        "routes": dict(Counter(row["evidence_mode"] for row in rows)),
        "country": "Rwanda",
        "admin_units_covered": sorted({f"{row['province']} / {row['district']} / {row['sector']}" for row in rows}),
        "files": {
            "master_csv": MASTER_CSV.name,
            "route_csvs": {route: path.name for route, path in ROUTE_FILES.items()},
            "bonus_text": BONUS_TXT.name,
            "desk_review_docx": REPORT_DOCX.name,
            "desk_review_pdf": REPORT_PDF.name,
        },
        "grounding_sources": [
            "AIMS-Imperial ClimateTales proposal, November 2025",
            "SNV ReCIC Rwanda clean cooking project",
            "RTI/PLOS One study on fuel pellets and improved cookstoves in Gisenyi",
            "DelAgua Tubeho Neza project materials",
            "SEforALL eCooking pilot in Kigali report",
            "Rwanda clean cooking RBF and EAQIP policy materials",
        ],
        "synthetic_data_notice": "Fictional test data for software validation only; not real human-subjects evidence.",
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_margin(cell, top=120, start=120, bottom=120, end=120):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for m, v in [("top", top), ("start", start), ("bottom", bottom), ("end", end)]:
        node = tc_mar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(v))
        node.set(qn("w:type"), "dxa")


def style_doc(doc: Document) -> None:
    styles = doc.styles
    styles["Normal"].font.name = "Aptos"
    styles["Normal"].font.size = Pt(10.5)
    styles["Normal"].paragraph_format.space_after = Pt(7)
    styles["Normal"].paragraph_format.line_spacing = 1.08
    for style_name, size, color in [
        ("Title", 24, RGBColor(22, 29, 43)),
        ("Heading 1", 16, RGBColor(45, 70, 115)),
        ("Heading 2", 13, RGBColor(77, 86, 100)),
        ("Heading 3", 11.5, RGBColor(77, 86, 100)),
    ]:
        style = styles[style_name]
        style.font.name = "Aptos Display"
        style.font.bold = True
        style.font.size = Pt(size)
        style.font.color.rgb = color


def add_doc_table(doc: Document, headers: list[str], body: list[list[str]], widths: list[float] | None = None) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    for idx, header in enumerate(headers):
        cell = table.rows[0].cells[idx]
        cell.text = header
        set_cell_shading(cell, "EAF0F8")
        set_cell_margin(cell)
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True
                run.font.size = Pt(9.5)
    for row in body:
        cells = table.add_row().cells
        for idx, value in enumerate(row):
            cells[idx].text = value
            cells[idx].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margin(cells[idx])
            for paragraph in cells[idx].paragraphs:
                paragraph.paragraph_format.space_after = Pt(2)
                for run in paragraph.runs:
                    run.font.size = Pt(9)
    if widths:
        for row in table.rows:
            for idx, width in enumerate(widths):
                row.cells[idx].width = Inches(width)
    doc.add_paragraph()


def add_callout(doc: Document, title: str, body: str) -> None:
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.rows[0].cells[0]
    set_cell_shading(cell, "F4F8F1")
    set_cell_margin(cell, 180, 180, 180, 180)
    p = cell.paragraphs[0]
    run = p.add_run(title)
    run.bold = True
    run.font.color.rgb = RGBColor(65, 92, 58)
    p.add_run("\n" + body)
    doc.add_paragraph()


def write_docx_report(rows: list[dict[str, str]]) -> None:
    doc = Document()
    style_doc(doc)
    section = doc.sections[0]
    section.top_margin = Cm(1.8)
    section.bottom_margin = Cm(1.8)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)

    title = doc.add_paragraph()
    title.style = "Title"
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.add_run("ClimateTales Rwanda and NDIM Engine").bold = True
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.add_run("Synthetic Narrative Corpus and Desk Review").bold = True
    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta.add_run(f"Generated {date.today().isoformat()} | Synthetic data for NDIM stress testing | Not field evidence")

    add_callout(
        doc,
        "Purpose",
        "This report documents the scientific rationale, design logic, and source grounding for a synthetic Rwanda clean-cooking narrative corpus built to test the NDIM Engine from narrative ingestion through policy output.",
    )

    doc.add_heading("Executive summary", level=1)
    doc.add_paragraph(
        "The #ClimateTales project asks whether culturally grounded narratives can improve clean climate technology adoption in Rwanda by linking social insight mining, behavioural design labs, a gamified influence simulator, and story activation pilots (AIMS-Imperial, 2025). The synthetic corpus created here translates that project logic into importable NDIM test data. It contains structured interviews, open stories, indigenous knowledge, citizen science reports, crowdsourced batches, and social media feed extracts."
    )
    doc.add_paragraph(
        "The corpus is designed to stress-test both the tool and the scientific workflow: SDMX-style coherence, consent and visibility metadata, approval governance, encoding variation, misinformation and inoculation opportunities, model feedback, and policy-facing interpretation. It is intentionally diverse across administrative locations, respondent roles, technology options, adoption stance, tone, trust, and barriers."
    )

    doc.add_heading("Thesis: narrative evidence is necessary for climate-technology adoption", level=1)
    doc.add_paragraph(
        "The proposal's core thesis is that clean-technology adoption is not only a technical or economic problem; it is also a narrative problem. Household cooking choices are embedded in routine, status, gendered labour, food texture, trust in messengers, perceived risk, and community proof. Rwanda clean-cooking literature supports this premise: studies of improved cookstoves and fuel pellets show that adoption depends on affordability, fuel supply, product confidence, after-sales support, and social learning, not only awareness (Seguin et al., 2018)."
    )
    doc.add_paragraph(
        "Clean cooking projects in Rwanda also operate through institutions and trust networks. ReCIC targets production, marketing, and use of improved cooking energy systems (SNV, 2024), while Tubeho Neza and related carbon-finance programmes connect cookstove distribution, maintenance, awareness, and emissions reductions (DelAgua, 2026; Ci-Dev, 2024). The NDIM workflow therefore needs narratives that reveal why a household accepts, delays, adapts, or refuses a clean-cooking intervention."
    )

    doc.add_heading("Antithesis: narrative data can mislead if it is not governed", level=1)
    doc.add_paragraph(
        "The counter-argument is equally important: stories are powerful but can be noisy, duplicated, biased, sensitive, or strategically manipulated. Social media feeds may amplify rumours faster than correction. Indigenous knowledge can be extracted without proper community validation. Crowdsourced evidence can include false narratives or low-quality submissions. For this reason, the corpus includes consent tiers, visibility, review status, source actor, trusted messenger, validation status, and tamper-evident workflow fields."
    )
    doc.add_paragraph(
        "The tool should not treat a narrative as policy evidence merely because it is vivid. It should ask: who said it, where, under what consent, whether it is locally grounded, how it was reviewed, whether it contains misinformation, and whether it should influence a model. This is why the synthetic dataset includes both adoption-positive and adoption-resistant stories."
    )

    doc.add_heading("Synthesis: governed narrative intelligence for decision support", level=1)
    doc.add_paragraph(
        "The synthesis is a governed narrative intelligence pipeline. Field and digital stories are first made coherent through a shared observation table. They then pass through SDMX-style metadata, approval, encoding, model simulation, inoculation testing, regional interpretation, and policy export. This turns narrative evidence into decision support without pretending that stories are the same as measured engineering data."
    )
    doc.add_paragraph(
        "The corpus was therefore created to test the whole chain: it includes clean-cooking technologies such as electric pressure cookers, improved biomass stoves, pellet stoves, LPG, briquettes, biogas, and repair-support interventions. It also includes communication channels such as savings groups, community health workers, school kitchens, radio drama, WhatsApp summaries, and youth climate catalysts."
    )

    doc.add_heading("Desk-review grounding", level=1)
    add_doc_table(
        doc,
        ["Source", "What it contributes", "How it shaped the corpus"],
        [
            ["AIMS-Imperial proposal (2025)", "ClimateTales vision: social insight mining, behavioural labs, digital twin simulator, story activation pilots.", "Data fields include source route, messenger, narrative body, intervention channel, and policy relevance."],
            ["Seguin et al. / RTI-PLOS One (2018)", "Qualitative evidence on barriers and facilitators for fuel pellets and improved cookstoves in Gisenyi.", "Narratives vary trust, payment, repair, contract confusion, taste, and fuel supply."],
            ["SNV ReCIC Rwanda", "Market and use challenges for improved cooking energy systems.", "Routes include market, supply-chain, and behaviour-change narratives."],
            ["DelAgua Tubeho Neza and Ci-Dev", "Improved cookstove distribution, carbon finance, maintenance, and awareness.", "Stories test household trust in distribution, maintenance, and programme continuity."],
            ["SEforALL eCooking pilot Kigali", "Electric pressure cooker and e-cooking usage evidence.", "Stories include EPC demonstrations, bills, power reliability, and food texture."],
            ["Rwanda RBF/EAQIP materials", "Clean cooking targets, subsidy logic, stove performance, and access policy.", "Records include policy-relevant fields for subsidy, cost, and transition friction."],
        ],
        widths=[1.8, 2.3, 2.7],
    )

    doc.add_heading("Dataset design", level=1)
    counts = Counter(row["evidence_mode"] for row in rows)
    add_doc_table(
        doc,
        ["Evidence route", "Rows", "Scientific purpose"],
        [
            ["Structured interview", str(counts["structured_interview"]), "Tests Q1-Q5 splitting, respondent profiles, and comparable enumerator protocols."],
            ["Open story", str(counts["open_story"]), "Tests multi-paragraph lived experience narratives."],
            ["Indigenous knowledge", str(counts["indigenous_knowledge"]), "Tests sensitivity, attribution, benefit sharing, and community validation."],
            ["Citizen science", str(counts["citizen_science"]), "Tests observation confidence, repeated behaviour, and local measurement claims."],
            ["Crowdsourced batch", str(counts["crowd_batch"]), "Tests batch queues, duplication review, approval, and commit workflows."],
            ["Social media feeds", str(counts["experimental_feed"]), "Tests digital listening, multi-platform feed metadata, and misinformation risk."],
        ],
        widths=[1.8, 0.7, 4.3],
    )

    doc.add_heading("Expected NDIM behaviours to test", level=1)
    doc.add_paragraph(
        "The scores in the corpus are not model outputs. They are calibration targets for stress-testing the encoder and the user interface. High misinformation risk combined with low trust should raise inoculation opportunity. High trust with low barrier strength should support adoption acceleration. Indigenous knowledge should be locally grounded but should require explicit community validation before policy claims."
    )
    add_doc_table(
        doc,
        ["Signal", "Expected tool behaviour"],
        [
            ["High barrier + high misinformation", "Recommend prebunk/refutational messaging and trusted messenger testing before model influence."],
            ["High trust + low barrier", "Treat as an acceleration opportunity and test peer-proof diffusion."],
            ["Sensitive indigenous knowledge", "Hold for community validation and restrict visibility until benefit-sharing is clear."],
            ["Social media feed", "Keep experimental status, require triangulation, and avoid direct policy claims before validation."],
            ["Citizen observation", "Use as situated evidence with confidence level and repeated-behaviour context."],
        ],
        widths=[2.0, 4.8],
    )

    doc.add_heading("Limitations and research ethics", level=1)
    doc.add_paragraph(
        "The corpus is synthetic. It should be used to test ingestion, governance, encoding, modelling, and reporting, not to make substantive claims about any named community. Real field use would require consent, data protection review, translation protocols, double coding, inter-rater reliability checks, community validation, and a clear process for returning insights to contributors."
    )
    doc.add_paragraph(
        "The report also does not replace a systematic literature review. It is a focused desk review intended to ground test-data design in plausible Rwanda clean-cooking contexts."
    )

    doc.add_heading("Generated files", level=1)
    file_rows = [["Combined corpus", MASTER_CSV.name, "60 rows across all routes"]]
    for route, path in ROUTE_FILES.items():
        file_rows.append([route, path.name, "10 rows"])
    file_rows.append(["Bonus story", BONUS_TXT.name, "Single TXT story for manual upload"])
    file_rows.append(["Desk review", REPORT_DOCX.name, "Editable DOCX report"])
    file_rows.append(["Desk review", REPORT_PDF.name, "Printable PDF report"])
    add_doc_table(doc, ["Item", "Filename", "Use"], file_rows, widths=[1.6, 3.0, 2.2])

    doc.add_heading("References", level=1)
    references = [
        "AIMS-Imperial. (2025). ClimateTales: Driving Clean Climate Tech Adoption Through Cultural Narratives in Rwanda. AIMS Partnerships Fund proposal.",
        "Ci-Dev. (2024). Rwanda: Clean and Improved Cooking DelAgua. https://www.ci-dev.org/programs/rwanda-clean-and-improved-cooking-delagua",
        "DelAgua. (2026). Project Rwanda: Tubeho Neza. https://www.delagua.org/project-rwanda/",
        "Rwanda Energy Group / EDCL. (2026). RBF Clean Cooking. https://www.reg.rw/what-we-do/rbf-programs/rbf-clean-cooking/",
        "Seguin, R., et al. (2018). Barriers and facilitators to adoption and use of fuel pellets and improved cookstoves in urban Rwanda. PLOS ONE / RTI. https://www.rti.org/publication/barriers-facilitators-adoption-use-fuel-pellets-improved-cookstoves-urban-rwanda",
        "SEforALL. (2023). Examining the experience of e-cooking pilot in Kigali, Rwanda. https://www.seforall.org/system/files/2023-11/report-rwanda-clean-cooking-Nov-10.pdf",
        "SNV. (2024). Reducing Climate Impact of Cooking in Rwanda through improved cooking energy systems (ReCIC). https://www.snv.org/project/reducing-climate-impact-of-cooking-in-rwanda-through-improved-cooking-energy-systems-recic",
        "WHO. (2023). Opportunities for transition to clean household energy in Rwanda. https://www.who.int/publications/i/item/9789240066625",
    ]
    for ref in references:
        p = doc.add_paragraph(ref, style="Normal")
        p.paragraph_format.left_indent = Cm(0.6)
        p.paragraph_format.first_line_indent = Cm(-0.6)

    doc.add_section(WD_SECTION.NEW_PAGE)
    doc.add_heading("Appendix: proposal signals extracted into corpus design", level=1)
    for item in [
        "Social insight mining: reflected through field notes, structured interviews, citizen reports, and social media feed records.",
        "Behavioural design labs: reflected through intervention_channel, trusted_messenger, and inoculation_opportunity fields.",
        "Gamified influence simulator: reflected through expected_ndim_signal and calibrated variation in trust, barriers, and misinformation.",
        "Story activation pilots: reflected through counter-message opportunities and local messenger recommendations.",
        "Community influencer training: reflected through youth catalysts, community health workers, teachers, elders, and savings-group leaders.",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.save(REPORT_DOCX)


def write_pdf_report(rows: list[dict[str, str]]) -> None:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Justified", parent=styles["BodyText"], alignment=TA_JUSTIFY, leading=14, spaceAfter=8))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.5, leading=11, spaceAfter=4))
    styles["Title"].fontName = "Helvetica-Bold"
    styles["Title"].fontSize = 20
    styles["Heading1"].fontSize = 14
    styles["Heading1"].spaceBefore = 12
    story = []
    doc = SimpleDocTemplate(
        str(REPORT_PDF),
        pagesize=A4,
        rightMargin=1.7 * cm,
        leftMargin=1.7 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm,
    )
    story.append(Paragraph("ClimateTales Rwanda and NDIM Engine", styles["Title"]))
    story.append(Paragraph("Synthetic Narrative Corpus and Desk Review", styles["Heading2"]))
    story.append(Paragraph(f"Generated {date.today().isoformat()} | Synthetic data for NDIM stress testing | Not field evidence", styles["Small"]))
    story.append(Spacer(1, 8))
    sections = [
        ("Executive summary", "The ClimateTales project asks whether culturally grounded narratives can improve clean climate technology adoption in Rwanda by linking social insight mining, behavioural design labs, a gamified influence simulator, and story activation pilots (AIMS-Imperial, 2025). This corpus translates that logic into importable NDIM test data."),
        ("Thesis", "Narrative evidence is necessary because household cooking choices are embedded in routine, status, gendered labour, food texture, trust in messengers, perceived risk, and community proof. Rwanda clean-cooking literature shows that adoption depends on affordability, supply, confidence, after-sales support, and social learning (Seguin et al., 2018; SNV, 2024)."),
        ("Antithesis", "Narrative data can mislead if it is not governed. Stories can be duplicated, sensitive, biased, or manipulated. The corpus therefore includes consent, visibility, validation status, source actor, trusted messenger, and review fields."),
        ("Synthesis", "The NDIM pathway should turn narratives into governed evidence: intake, SDMX-style metadata, approval, encoding, simulation, inoculation testing, regional interpretation, and policy export."),
        ("Limitations", "These records are fictional and intended only for software and workflow stress testing. Real use requires consent, translation protocols, double coding, community validation, and human review."),
    ]
    for heading, body in sections:
        story.append(Paragraph(heading, styles["Heading1"]))
        story.append(Paragraph(body, styles["Justified"]))
    counts = Counter(row["evidence_mode"] for row in rows)
    table_data = [["Evidence route", "Rows", "Purpose"]]
    for route, count in counts.items():
        table_data.append([route, str(count), "Stress-tests route-specific intake, metadata, governance, encoding, and policy interpretation."])
    table = Table(table_data, colWidths=[4.2 * cm, 1.4 * cm, 10.0 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF0F8")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B9C3D4")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(Paragraph("Dataset design", styles["Heading1"]))
    story.append(table)
    story.append(PageBreak())
    story.append(Paragraph("References", styles["Heading1"]))
    refs = [
        "AIMS-Imperial. (2025). ClimateTales: Driving Clean Climate Tech Adoption Through Cultural Narratives in Rwanda. AIMS Partnerships Fund proposal.",
        "Ci-Dev. (2024). Rwanda: Clean and Improved Cooking DelAgua. https://www.ci-dev.org/programs/rwanda-clean-and-improved-cooking-delagua",
        "DelAgua. (2026). Project Rwanda: Tubeho Neza. https://www.delagua.org/project-rwanda/",
        "Rwanda Energy Group / EDCL. (2026). RBF Clean Cooking. https://www.reg.rw/what-we-do/rbf-programs/rbf-clean-cooking/",
        "Seguin, R., et al. (2018). Barriers and facilitators to adoption and use of fuel pellets and improved cookstoves in urban Rwanda. https://www.rti.org/publication/barriers-facilitators-adoption-use-fuel-pellets-improved-cookstoves-urban-rwanda",
        "SEforALL. (2023). Examining the experience of e-cooking pilot in Kigali, Rwanda. https://www.seforall.org/system/files/2023-11/report-rwanda-clean-cooking-Nov-10.pdf",
        "SNV. (2024). Reducing Climate Impact of Cooking in Rwanda through improved cooking energy systems. https://www.snv.org/project/reducing-climate-impact-of-cooking-in-rwanda-through-improved-cooking-energy-systems-recic",
        "WHO. (2023). Opportunities for transition to clean household energy in Rwanda. https://www.who.int/publications/i/item/9789240066625",
    ]
    for ref in refs:
        story.append(Paragraph(ref, styles["Small"]))
    doc.build(story)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = make_rows()
    write_csv(MASTER_CSV, rows)
    for route, path in ROUTE_FILES.items():
        write_csv(path, [row for row in rows if row["evidence_mode"] == route])
    write_bonus_story()
    write_manifest(rows)
    write_readme(rows)
    write_docx_report(rows)
    write_pdf_report(rows)
    print(json.dumps({
        "records": len(rows),
        "routes": dict(Counter(row["evidence_mode"] for row in rows)),
        "master_csv": str(MASTER_CSV),
        "docx": str(REPORT_DOCX),
        "pdf": str(REPORT_PDF),
    }, indent=2))


if __name__ == "__main__":
    main()
