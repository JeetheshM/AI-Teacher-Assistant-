"""
Teaching Package PDF Export Service (Person 6)

Generates clean, professional, teacher-facing PDF teaching packages from structured application data.
Features:
- Deterministic, zero-LLM rendering.
- Robust handling of partial or missing sections (lesson-only, quiz-only, activity-only, no sources).
- Clean typographic styling, page numbering, and structured section flow.
- Path sanitization to prevent directory traversal.
"""

import os
import re
from typing import Dict, Any, Optional, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
    ListFlowable,
    ListItem,
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and render total page count and footer."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "TeachMate AI — Classroom Teaching Package")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Footer (all pages)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_str)
        self.drawString(54, 36, "Confidential — Prepared for Educator Use | Powered by TeachMate AI")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)

        self.restoreState()


class ExportService:
    """
    Exports structured teaching packages to PDF.
    """

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Sanitizes filename against path traversal and unsupported characters."""
        clean = re.sub(r"[^\w\-]", "_", name.strip())
        clean = re.sub(r"_+", "_", clean).strip("_")
        return clean or "teaching_package"

    def _get_styles(self) -> Dict[str, ParagraphStyle]:
        """Builds cohesive typography palette for the teaching package."""
        base_styles = getSampleStyleSheet()
        
        styles = {
            "DocTitle": ParagraphStyle(
                "DocTitle",
                parent=base_styles["Title"],
                fontName="Helvetica-Bold",
                fontSize=22,
                leading=26,
                textColor=colors.HexColor("#1A365D"),
                alignment=0,
                spaceAfter=4,
            ),
            "DocSubtitle": ParagraphStyle(
                "DocSubtitle",
                parent=base_styles["Normal"],
                fontName="Helvetica",
                fontSize=11,
                leading=15,
                textColor=colors.HexColor("#4A5568"),
                spaceAfter=12,
            ),
            "SectionHeader": ParagraphStyle(
                "SectionHeader",
                parent=base_styles["Heading1"],
                fontName="Helvetica-Bold",
                fontSize=14,
                leading=18,
                textColor=colors.HexColor("#2B6CB0"),
                spaceBefore=12,
                spaceAfter=6,
                keepWithNext=True,
            ),
            "SubSectionHeader": ParagraphStyle(
                "SubSectionHeader",
                parent=base_styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=11,
                leading=14,
                textColor=colors.HexColor("#2D3748"),
                spaceBefore=8,
                spaceAfter=3,
                keepWithNext=True,
            ),
            "Body": ParagraphStyle(
                "CustomBody",
                parent=base_styles["Normal"],
                fontName="Helvetica",
                fontSize=9.5,
                leading=13.5,
                textColor=colors.HexColor("#2D3748"),
                spaceAfter=4,
            ),
            "BodyBold": ParagraphStyle(
                "CustomBodyBold",
                parent=base_styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=9.5,
                leading=13.5,
                textColor=colors.HexColor("#1A202C"),
                spaceAfter=3,
            ),
            "Callout": ParagraphStyle(
                "Callout",
                parent=base_styles["Normal"],
                fontName="Helvetica-Oblique",
                fontSize=9,
                leading=13,
                textColor=colors.HexColor("#2C5282"),
            ),
            "MetaKey": ParagraphStyle(
                "MetaKey",
                parent=base_styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=9,
                leading=12,
                textColor=colors.HexColor("#4A5568"),
            ),
            "MetaVal": ParagraphStyle(
                "MetaVal",
                parent=base_styles["Normal"],
                fontName="Helvetica",
                fontSize=9,
                leading=12,
                textColor=colors.HexColor("#1A202C"),
            ),
            "Badge": ParagraphStyle(
                "Badge",
                parent=base_styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=8,
                leading=10,
                textColor=colors.HexColor("#2B6CB0"),
            ),
        }
        return styles

    def generate_pdf(
        self,
        teaching_package: Dict[str, Any],
        output_path: Optional[str] = None,
    ) -> str:
        """
        Generates a PDF from the given teaching package dictionary.
        Returns the absolute path to the generated PDF.
        """
        if not isinstance(teaching_package, dict):
            raise ValueError("teaching_package must be a dictionary.")

        # Determine target output path
        lesson_data = teaching_package.get("lesson") or {}
        topic = lesson_data.get("topic") or teaching_package.get("topic") or "Teaching_Package"
        grade = lesson_data.get("grade") or teaching_package.get("grade") or ""
        
        default_filename = f"{self.sanitize_filename(f'{topic}_Grade_{grade}')}.pdf"
        
        if output_path is None:
            output_dir = os.path.join(os.getcwd(), "exports")
            os.makedirs(output_dir, exist_ok=True)
            target_file = os.path.join(output_dir, default_filename)
        else:
            # Ensure safe output path
            target_file = os.path.abspath(output_path)
            os.makedirs(os.path.dirname(target_file), exist_ok=True)

        doc = SimpleDocTemplate(
            target_file,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54,
        )

        styles = self._get_styles()
        story = []

        # 1. Header Banner
        subject = lesson_data.get("subject") or teaching_package.get("subject") or "General Subject"
        title = lesson_data.get("title") or f"{topic} — Complete Teaching Package"
        
        story.append(Paragraph("TEACHMATE AI", styles["DocSubtitle"]))
        story.append(Paragraph(title, styles["DocTitle"]))
        story.append(Paragraph(f"Subject: <b>{subject}</b> | Grade: <b>{grade or 'N/A'}</b> | Curriculum-Grounded Educator Package", styles["DocSubtitle"]))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2B6CB0"), spaceAfter=10))

        # 2. Metadata Box
        duration = lesson_data.get("duration_minutes") or lesson_data.get("total_duration_minutes") or teaching_package.get("duration_minutes") or "45"
        difficulty = lesson_data.get("difficulty") or teaching_package.get("difficulty") or "Intermediate"
        objective = lesson_data.get("learning_objective") or teaching_package.get("learning_objective") or ""
        
        meta_table_data = [
            [
                Paragraph("<b>Subject:</b>", styles["MetaKey"]),
                Paragraph(str(subject), styles["MetaVal"]),
                Paragraph("<b>Duration:</b>", styles["MetaKey"]),
                Paragraph(f"{duration} mins", styles["MetaVal"]),
            ],
            [
                Paragraph("<b>Topic:</b>", styles["MetaKey"]),
                Paragraph(str(topic), styles["MetaVal"]),
                Paragraph("<b>Difficulty:</b>", styles["MetaKey"]),
                Paragraph(str(difficulty).capitalize(), styles["MetaVal"]),
            ],
        ]
        
        meta_table = Table(meta_table_data, colWidths=[65, 185, 65, 185])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#EDF2F7")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 8))

        # 3. Learning Objectives
        objectives = lesson_data.get("objectives") or ([objective] if objective else [])
        if objectives:
            story.append(Paragraph("Learning Objectives", styles["SectionHeader"]))
            for obj in objectives:
                if isinstance(obj, str) and obj.strip():
                    story.append(Paragraph(f"• {obj}", styles["Body"]))
            story.append(Spacer(1, 6))

        # 4. Prerequisites (if any)
        prerequisites = lesson_data.get("prerequisites") or []
        if prerequisites:
            story.append(Paragraph("Prerequisites", styles["SubSectionHeader"]))
            for prereq in prerequisites:
                story.append(Paragraph(f"• {prereq}", styles["Body"]))
            story.append(Spacer(1, 6))

        # 5. Lesson Plan Components
        has_lesson_content = any([
            lesson_data.get("introduction"),
            lesson_data.get("explanation"),
            lesson_data.get("key_points"),
            lesson_data.get("examples"),
            lesson_data.get("common_misconceptions"),
            lesson_data.get("recap"),
        ])

        if has_lesson_content:
            story.append(Paragraph("Lesson Plan & Instructional Flow", styles["SectionHeader"]))

            # Introduction
            intro = lesson_data.get("introduction")
            if intro:
                intro_content = intro.get("content", str(intro)) if isinstance(intro, dict) else str(intro)
                intro_dur = f" ({intro.get('duration_minutes')} min)" if isinstance(intro, dict) and intro.get("duration_minutes") else ""
                story.append(Paragraph(f"<b>Introduction{intro_dur}:</b>", styles["SubSectionHeader"]))
                story.append(Paragraph(intro_content, styles["Body"]))

            # Core Explanation
            explanation = lesson_data.get("explanation")
            if explanation:
                exp_content = explanation.get("content", str(explanation)) if isinstance(explanation, dict) else str(explanation)
                exp_dur = f" ({explanation.get('duration_minutes')} min)" if isinstance(explanation, dict) and explanation.get("duration_minutes") else ""
                story.append(Paragraph(f"<b>Detailed Explanation{exp_dur}:</b>", styles["SubSectionHeader"]))
                story.append(Paragraph(exp_content, styles["Body"]))

            # Key Points
            key_points = lesson_data.get("key_points") or []
            if key_points:
                story.append(Paragraph("<b>Key Conceptual Points:</b>", styles["SubSectionHeader"]))
                for kp in key_points:
                    story.append(Paragraph(f"✓ {kp}", styles["Body"]))

            # Examples / Real-World Analogies
            examples = lesson_data.get("examples") or []
            if examples:
                story.append(Paragraph("<b>Real-World Examples & Analogies:</b>", styles["SubSectionHeader"]))
                for ex in examples:
                    story.append(Paragraph(f"💡 {ex}", styles["Body"]))

            # Common Misconceptions
            misconceptions = lesson_data.get("common_misconceptions") or []
            if misconceptions:
                story.append(Paragraph("<b>Common Misconceptions & Corrections:</b>", styles["SubSectionHeader"]))
                for mc in misconceptions:
                    story.append(Paragraph(f"⚠️ {mc}", styles["Body"]))

            # Recap
            recap = lesson_data.get("recap")
            if recap:
                story.append(Paragraph("<b>Summary / Recap:</b>", styles["SubSectionHeader"]))
                story.append(Paragraph(str(recap), styles["Body"]))

            story.append(Spacer(1, 8))

        # 6. Materials / Simplifications / Analogies (if standalone in materials dict)
        materials_dict = teaching_package.get("materials") or {}
        if isinstance(materials_dict, dict):
            simp = materials_dict.get("simplified_explanation") or materials_dict.get("explanation")
            if simp and isinstance(simp, (str, dict)) and simp != lesson_data.get("explanation"):
                content = simp if isinstance(simp, str) else simp.get("content", "")
                if content:
                    story.append(Paragraph("Simplified Explanation (Quick Reference)", styles["SectionHeader"]))
                    story.append(Paragraph(content, styles["Body"]))
                    story.append(Spacer(1, 6))

        # 7. Classroom Activity
        activity_data = None
        if "activity" in teaching_package:
            activity_data = teaching_package["activity"]
        elif isinstance(materials_dict, dict) and "activity" in materials_dict:
            activity_data = materials_dict["activity"]

        if activity_data and isinstance(activity_data, dict):
            story.append(Paragraph("Classroom Activity", styles["SectionHeader"]))
            
            act_title = activity_data.get("title", "Interactive Classroom Exercise")
            act_type = str(activity_data.get("activity_type", "Group")).capitalize()
            act_dur = activity_data.get("duration_minutes", 15)
            act_group = activity_data.get("group_size")
            group_str = f" | Group Size: {act_group} students" if act_group else ""

            story.append(Paragraph(f"<b>{act_title}</b> ({act_type} Activity | {act_dur} minutes{group_str})", styles["SubSectionHeader"]))
            
            if activity_data.get("objective"):
                story.append(Paragraph(f"<b>Objective:</b> {activity_data['objective']}", styles["Body"]))

            # Materials Table / List
            mat_list = activity_data.get("materials") or []
            if mat_list:
                story.append(Paragraph(f"<b>Materials Needed:</b> {', '.join(mat_list)}", styles["Body"]))

            if activity_data.get("setup"):
                story.append(Paragraph(f"<b>Setup:</b> {activity_data['setup']}", styles["Body"]))

            # Step-by-Step Instructions
            instructions = activity_data.get("instructions") or []
            if instructions:
                story.append(Paragraph("<b>Step-by-Step Instructions:</b>", styles["SubSectionHeader"]))
                for idx, step in enumerate(instructions, 1):
                    story.append(Paragraph(f"{idx}. {step}", styles["Body"]))

            # Roles & Outcomes
            if activity_data.get("teacher_role"):
                story.append(Paragraph(f"<b>Teacher's Role:</b> {activity_data['teacher_role']}", styles["Body"]))
            if activity_data.get("student_role"):
                story.append(Paragraph(f"<b>Student's Role:</b> {activity_data['student_role']}", styles["Body"]))
            if activity_data.get("expected_outcome"):
                story.append(Paragraph(f"<b>Expected Outcome:</b> {activity_data['expected_outcome']}", styles["Body"]))
            if activity_data.get("assessment_method"):
                story.append(Paragraph(f"<b>Assessment Method:</b> {activity_data['assessment_method']}", styles["Body"]))

            # Safety Notes
            safety = activity_data.get("safety_notes") or []
            if safety:
                story.append(Paragraph("<b>Safety Precautions:</b>", styles["SubSectionHeader"]))
                for s in safety:
                    story.append(Paragraph(f"🛡️ {s}", styles["Body"]))

            # Adaptations
            adaptations = activity_data.get("adaptations") or []
            if adaptations:
                story.append(Paragraph("<b>Adaptations & Differentiation:</b>", styles["SubSectionHeader"]))
                for ad in adaptations:
                    story.append(Paragraph(f"• {ad}", styles["Body"]))

            story.append(Spacer(1, 8))

        # 8. Quiz
        quiz_data = teaching_package.get("quiz") or {}
        questions = quiz_data.get("questions") or []
        if questions:
            story.append(Paragraph(f"Assessment Quiz — {quiz_data.get('title', topic)}", styles["SectionHeader"]))
            
            for idx, q in enumerate(questions, 1):
                q_text = q.get("question") or q.get("question_text") or f"Question {idx}"
                q_type = str(q.get("type") or q.get("question_type") or "mcq").upper()
                bloom = str(q.get("bloom_level") or "").capitalize()
                bloom_tag = f" [{bloom}]" if bloom else ""

                story.append(Paragraph(f"<b>Q{idx}. ({q_type}{bloom_tag}) {q_text}</b>", styles["BodyBold"]))

                # Options if MCQ
                options = q.get("options") or []
                if options and isinstance(options, list):
                    for opt_idx, opt in enumerate(options):
                        letter_opt = chr(65 + opt_idx)
                        story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;<b>{letter_opt}.</b> {opt}", styles["Body"]))
                story.append(Spacer(1, 3))

            story.append(Spacer(1, 8))

            # 9. Answer Key (Directly extracted from quiz questions, no LLM call)
            story.append(Paragraph("Answer Key & Explanations (Teacher Reference)", styles["SectionHeader"]))
            for idx, q in enumerate(questions, 1):
                ans = q.get("correct_answer") or "N/A"
                exp = q.get("explanation") or "No explanation provided."
                story.append(Paragraph(f"<b>Q{idx} Answer:</b> {ans}", styles["BodyBold"]))
                story.append(Paragraph(f"<b>Explanation:</b> {exp}", styles["Callout"]))
                story.append(Spacer(1, 2))

            story.append(Spacer(1, 8))

        # 10. Sources Used / Curriculum Grounding
        sources = teaching_package.get("sources") or []
        if not sources and activity_data and isinstance(activity_data, dict):
            sources = activity_data.get("sources_used") or []

        if sources:
            story.append(Paragraph("Curriculum Sources & References", styles["SectionHeader"]))
            for s in sources:
                if isinstance(s, dict):
                    src_name = s.get("source") or s.get("filename") or "Curriculum Document"
                    page = s.get("page_number")
                    page_str = f" — Page {page}" if page is not None else ""
                    story.append(Paragraph(f"📄 <b>{src_name}</b>{page_str}", styles["Body"]))
                elif isinstance(s, str):
                    story.append(Paragraph(f"📄 {s}", styles["Body"]))
            story.append(Spacer(1, 6))

        # Build document with NumberedCanvas
        doc.build(story, canvasmaker=NumberedCanvas)
        return target_file
