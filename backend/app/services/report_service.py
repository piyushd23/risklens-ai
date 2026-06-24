import os
import json
from datetime import datetime
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class ReportService:
    @staticmethod
    def get_reports_dir() -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        reports_dir = os.path.join(base_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        return reports_dir

    @classmethod
    def generate_json(cls, target_name: str, target_url: str, started_at: datetime, 
                      security_score: float, compliance_score: float, 
                      findings: List[Dict[str, Any]]) -> str:
        report_data = {
            "platform": "RiskLens AI",
            "generation_time": datetime.utcnow().isoformat(),
            "target": {
                "name": target_name,
                "url": target_url
            },
            "metrics": {
                "security_score": security_score,
                "compliance_score": compliance_score,
                "total_findings": len(findings)
            },
            "findings": findings
        }
        
        filename = f"report_{target_name.replace(' ', '_')}_{int(datetime.utcnow().timestamp())}.json"
        file_path = os.path.join(cls.get_reports_dir(), filename)
        
        with open(file_path, "w") as f:
            json.dump(report_data, f, indent=2)
            
        return file_path

    @classmethod
    def generate_html(cls, target_name: str, target_url: str, started_at: datetime, 
                      security_score: float, compliance_score: float, 
                      findings: List[Dict[str, Any]]) -> str:
        
        findings_html = ""
        for idx, f in enumerate(findings):
            sev_colors = {
                "Critical": "#FEE2E2", "High": "#FFEDD5", 
                "Medium": "#FEF3C7", "Low": "#F0FDF4"
            }
            sev_text_colors = {
                "Critical": "#991B1B", "High": "#9A3412", 
                "Medium": "#92400E", "Low": "#166534"
            }
            
            sev = f.get("severity", "Low")
            bg = sev_colors.get(sev, "#F0FDF4")
            txt = sev_text_colors.get(sev, "#166534")
            
            findings_html += f"""
            <div class="finding-card">
                <div class="finding-header">
                    <span class="finding-title">{idx+1}. {f.get('title')}</span>
                    <span class="severity-badge" style="background-color: {bg}; color: {txt}">{sev} (CVSS {f.get('cvss_score')})</span>
                </div>
                <div class="finding-meta">
                    <strong>OWASP Category:</strong> {f.get('owasp_category')} | 
                    <strong>Confidence:</strong> {f.get('confidence_level')}
                </div>
                <div class="finding-detail">
                    <p><strong>Description:</strong> {f.get('description')}</p>
                    <p><strong>Evidence:</strong> <code class="evidence-block">{f.get('evidence')}</code></p>
                    <p><strong>Risk Explanation:</strong> {f.get('risk_explanation')}</p>
                    <p><strong>Remediation Guidance:</strong> {f.get('remediation_guidance')}</p>
                </div>
            </div>
            """
            
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>RiskLens AI Security Report - {target_name}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #FAFAFA; color: #1F2937; margin: 0; padding: 0; }}
                .container {{ max-width: 900px; margin: 40px auto; background-color: #FFFFFF; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #22C55E; padding-bottom: 20px; margin-bottom: 30px; }}
                .title-block h1 {{ margin: 0; color: #14532D; font-size: 28px; }}
                .tagline {{ color: #22C55E; font-weight: 600; margin-top: 5px; }}
                .meta-table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
                .meta-table td {{ padding: 8px 12px; border: 1px solid #E5E7EB; }}
                .meta-table td.label {{ font-weight: bold; background-color: #F9FAFB; width: 25%; }}
                .metrics-row {{ display: flex; gap: 20px; margin-bottom: 40px; }}
                .metric-card {{ flex: 1; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid #DCFCE7; }}
                .metric-card.security {{ background-color: #F0FDF4; }}
                .metric-card.compliance {{ background-color: #ECFDF5; }}
                .metric-val {{ font-size: 36px; font-weight: bold; color: #14532D; margin-top: 10px; }}
                .finding-card {{ background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; margin-bottom: 25px; overflow: hidden; }}
                .finding-header {{ display: flex; justify-content: space-between; align-items: center; background-color: #F9FAFB; padding: 15px 20px; border-bottom: 1px solid #E5E7EB; }}
                .finding-title {{ font-size: 18px; font-weight: bold; color: #111827; }}
                .severity-badge {{ padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: bold; }}
                .finding-meta {{ padding: 10px 20px; font-size: 13px; color: #6B7280; border-bottom: 1px solid #F3F4F6; }}
                .finding-detail {{ padding: 20px; }}
                .finding-detail p {{ margin: 0 0 15px 0; line-height: 1.5; }}
                .evidence-block {{ display: block; background-color: #F3F4F6; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 13px; border-left: 3px solid #6B7280; word-break: break-all; white-space: pre-wrap; }}
                .footer {{ text-align: center; margin-top: 50px; font-size: 12px; color: #9CA3AF; border-top: 1px solid #E5E7EB; padding-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="title-block">
                        <h1>RiskLens AI</h1>
                        <div class="tagline">Intelligent Security Assessment. Actionable Risk Insights.</div>
                    </div>
                    <div style="text-align: right; font-size: 12px; color: #6B7280;">
                        Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
                    </div>
                </div>
                
                <h2>Assessment Overview</h2>
                <table class="meta-table">
                    <tr>
                        <td class="label">Target Name</td>
                        <td>{target_name}</td>
                        <td class="label">Start URL</td>
                        <td><a href="{target_url}" target="_blank">{target_url}</a></td>
                    </tr>
                    <tr>
                        <td class="label">Environment</td>
                        <td>Production Sandbox</td>
                        <td class="label">Assessment Type</td>
                        <td>Defensive Web Audit (DAST)</td>
                    </tr>
                </table>
                
                <div class="metrics-row">
                    <div class="metric-card security">
                        <div style="color: #166534; font-weight: 600;">Overall Security Score</div>
                        <div class="metric-val">{security_score:.1f}/100</div>
                    </div>
                    <div class="metric-card compliance">
                        <div style="color: #065F46; font-weight: 600;">OWASP Compliance Score</div>
                        <div class="metric-val">{compliance_score:.1f}%</div>
                    </div>
                    <div class="metric-card" style="background-color: #F9FAFB;">
                        <div style="color: #374151; font-weight: 600;">Total Weaknesses</div>
                        <div class="metric-val">{len(findings)}</div>
                    </div>
                </div>
                
                <h2>Discovered Weaknesses ({len(findings)})</h2>
                {findings_html if findings else '<p style="color: #6B7280; text-align: center; padding: 20px;">No findings detected on this target.</p>'}
                
                <div class="footer">
                    RiskLens AI &bull; Strictly Defensive Vulnerability Management &bull; Confidential Security Document
                </div>
            </div>
        </body>
        </html>
        """
        
        filename = f"report_{target_name.replace(' ', '_')}_{int(datetime.utcnow().timestamp())}.html"
        file_path = os.path.join(cls.get_reports_dir(), filename)
        
        with open(file_path, "w") as f:
            f.write(html_content)
            
        return file_path

    @classmethod
    def generate_pdf(cls, target_name: str, target_url: str, started_at: datetime, 
                      security_score: float, compliance_score: float, 
                      findings: List[Dict[str, Any]]) -> str:
        
        filename = f"report_{target_name.replace(' ', '_')}_{int(datetime.utcnow().timestamp())}.pdf"
        file_path = os.path.join(cls.get_reports_dir(), filename)
        
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
        )
        
        styles = getSampleStyleSheet()
        
        # Define clean, green enterprise styles
        title_style = ParagraphStyle(
            name="CoverTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=34,
            textColor=colors.HexColor("#14532D"),
            spaceAfter=10
        )
        
        subtitle_style = ParagraphStyle(
            name="CoverSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#22C55E"),
            spaceAfter=30
        )
        
        section_style = ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#14532D"),
            spaceBefore=15,
            spaceAfter=10,
            keepWithNext=True
        )
        
        body_style = ParagraphStyle(
            name="ReportBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#1F2937")
        )
        
        code_style = ParagraphStyle(
            name="ReportCode",
            parent=styles["Code"],
            fontName="Courier",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#374151")
        )
        
        story = []
        
        # 1. COVER PAGE
        story.append(Spacer(1, 100))
        story.append(Paragraph("RiskLens AI", title_style))
        story.append(Paragraph("AI-Driven Security Risk Analytics Platform", subtitle_style))
        story.append(Spacer(1, 40))
        
        story.append(Paragraph("<b>CONFIDENTIAL SECURITY REPORT</b>", body_style))
        story.append(Spacer(1, 10))
        
        # Details Table
        meta_data = [
            [Paragraph("<b>Target Name:</b>", body_style), Paragraph(target_name, body_style)],
            [Paragraph("<b>Target URL:</b>", body_style), Paragraph(target_url, body_style)],
            [Paragraph("<b>Generated:</b>", body_style), Paragraph(datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'), body_style)],
            [Paragraph("<b>Security Score:</b>", body_style), Paragraph(f"{security_score:.1f} / 100", body_style)],
            [Paragraph("<b>Compliance Score:</b>", body_style), Paragraph(f"{compliance_score:.1f}%", body_style)],
            [Paragraph("<b>Total Weaknesses:</b>", body_style), Paragraph(str(len(findings)), body_style)],
        ]
        
        t = Table(meta_data, colWidths=[120, 300])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0FDF4")),
            ('PADDING', (0,0), (-1,-1), 8),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#DCFCE7")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t)
        
        story.append(PageBreak())
        
        # 2. EXECUTIVE SUMMARY
        story.append(Paragraph("Executive Overview", section_style))
        exec_text = (
            "This report documents the security posture assessment performed using the RiskLens AI Platform. "
            "The platform crawled available endpoints and analyzed server configuration headers, cookie configurations, "
            "form structures, and transport encryption. "
            "Critical and high risks should be addressed immediately to ensure robust cyber defense posture."
        )
        story.append(Paragraph(exec_text, body_style))
        story.append(Spacer(1, 20))
        
        # 3. FINDINGS LISTING
        story.append(Paragraph("Detailed Findings & Recommendations", section_style))
        
        if not findings:
            story.append(Paragraph("No vulnerabilities were identified during this assessment.", body_style))
        else:
            for idx, f in enumerate(findings):
                # Severity Color
                sev = f.get("severity", "Low")
                if sev == "Critical":
                    color_bg = colors.HexColor("#FEE2E2")
                elif sev == "High":
                    color_bg = colors.HexColor("#FFEDD5")
                elif sev == "Medium":
                    color_bg = colors.HexColor("#FEF3C7")
                else:
                    color_bg = colors.HexColor("#F0FDF4")
                    
                finding_data = [
                    [Paragraph(f"<b>{idx+1}. {f.get('title')}</b>", body_style), 
                     Paragraph(f"<b>Severity: {sev} (CVSS {f.get('cvss_score')})</b>", body_style)],
                    [Paragraph(f"<b>OWASP Category:</b> {f.get('owasp_category')}", body_style), ""],
                    [Paragraph(f"<b>Description:</b> {f.get('description')}", body_style), ""],
                    [Paragraph(f"<b>Evidence:</b>", body_style), ""],
                    [Paragraph(f"{f.get('evidence')}", code_style), ""],
                    [Paragraph(f"<b>Risk Impact:</b> {f.get('risk_explanation')}", body_style), ""],
                    [Paragraph(f"<b>Remediation:</b> {f.get('remediation_guidance')}", body_style), ""]
                ]
                
                ft = Table(finding_data, colWidths=[250, 250])
                ft.setStyle(TableStyle([
                    ('SPAN', (0, 1), (1, 1)),
                    ('SPAN', (0, 2), (1, 2)),
                    ('SPAN', (0, 3), (1, 3)),
                    ('SPAN', (0, 4), (1, 4)),
                    ('SPAN', (0, 5), (1, 5)),
                    ('SPAN', (0, 6), (1, 6)),
                    ('BACKGROUND', (0,0), (-1,0), color_bg),
                    ('PADDING', (0,0), (-1,-1), 6),
                    ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
                    ('LINEBELOW', (0,0), (-1,0), 0.5, colors.HexColor("#E5E7EB")),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ]))
                
                story.append(KeepTogether([ft, Spacer(1, 15)]))
                
        doc.build(story)
        return file_path
