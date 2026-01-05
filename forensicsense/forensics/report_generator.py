"""
Professional report generation for forensic analysis

Generates comprehensive reports in multiple formats:
- PDF (professional)
- JSON (machine-readable)
- HTML (web view)
- Markdown (lightweight)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from ..utils.logging import get_logger

logger = get_logger('report_generator')


class ReportGenerator:
    """Generate professional forensic reports"""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("reports")
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
    def generate_report(
        self,
        profile: Dict,
        format: str = 'json',
        output_file: Optional[str] = None
    ) -> Path:
        """
        Generate forensic report
        
        Args:
            profile: Target profile data
            format: Output format ('json', 'html', 'md', 'pdf')
            output_file: Optional output filename
            
        Returns:
            Path to generated report
        """
        logger.info(f"Generating {format} report")
        
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            target = profile.get('target', 'unknown').replace('/', '_').replace(':', '_')
            output_file = f"report_{target}_{timestamp}.{format}"
        
        output_path = self.output_dir / output_file
        
        if format == 'json':
            self._generate_json(profile, output_path)
        elif format == 'html':
            self._generate_html(profile, output_path)
        elif format == 'md':
            self._generate_markdown(profile, output_path)
        elif format == 'pdf':
            self._generate_pdf(profile, output_path)
        else:
            raise ValueError(f"Unknown format: {format}")
        
        logger.info(f"Report generated: {output_path}")
        return output_path
    
    def _generate_json(self, profile: Dict, output_path: Path):
        """Generate JSON report"""
        with open(output_path, 'w') as f:
            json.dump(profile, f, indent=2, default=str)
    
    def _generate_markdown(self, profile: Dict, output_path: Path):
        """Generate Markdown report"""
        md = []
        
        # Header
        md.append(f"# Forensic Analysis Report")
        md.append(f"\n**Target:** {profile.get('target')}")
        md.append(f"**Profile Depth:** {profile.get('profile_depth')}")
        md.append(f"**Started:** {profile.get('started_at')}")
        md.append(f"**Completed:** {profile.get('completed_at')}")
        md.append("")
        
        # Executive Summary
        md.append("## Executive Summary")
        md.append("")
        risk = profile.get('risk_assessment', {})
        md.append(f"**Risk Level:** {risk.get('level', 'UNKNOWN')}")
        md.append(f"**Risk Score:** {risk.get('score', 0)}/100")
        md.append("")
        
        # DNS Information
        md.append("## DNS Information")
        md.append("")
        dns_info = profile.get('dns_info', {})
        if dns_info.get('a_records'):
            md.append(f"**A Records:** {', '.join(dns_info['a_records'])}")
        if dns_info.get('mx_records'):
            md.append(f"**MX Records:** {len(dns_info['mx_records'])} found")
        md.append("")
        
        # Network Scan
        network_scan = profile.get('network_scan', {})
        if network_scan:
            md.append("## Network Scan")
            md.append("")
            open_ports = network_scan.get('open_ports', [])
            md.append(f"**Open Ports:** {len(open_ports)}")
            md.append("")
            if open_ports:
                md.append("| Port | Service | State | Banner |")
                md.append("|------|---------|-------|--------|")
                for port in open_ports[:20]:  # Limit to first 20
                    banner = port.get('banner', '')[:50] if port.get('banner') else 'N/A'
                    md.append(f"| {port['port']} | {port.get('service', 'unknown')} | {port['state']} | {banner} |")
            md.append("")
        
        # HTTP Fingerprint
        http_fp = profile.get('http_fingerprint', {})
        if http_fp and http_fp.get('status_code'):
            md.append("## HTTP Fingerprint")
            md.append("")
            md.append(f"**Status:** {http_fp.get('status_code')}")
            md.append(f"**Server:** {http_fp.get('server', 'Unknown')}")
            md.append(f"**Title:** {http_fp.get('title', 'N/A')}")
            md.append("")
            
            technologies = http_fp.get('technologies', [])
            if technologies:
                md.append("**Technologies Detected:**")
                for tech in technologies:
                    md.append(f"- {tech.get('name')} ({tech.get('confidence', 'unknown')} confidence)")
                md.append("")
        
        # OSINT
        osint = profile.get('osint', {})
        if osint:
            md.append("## OSINT Findings")
            md.append("")
            md.append(f"**Subdomains Found:** {osint.get('subdomain_count', 0)}")
            
            whois = osint.get('whois', {})
            if whois.get('registrar'):
                md.append(f"**Registrar:** {whois['registrar']}")
            md.append("")
        
        # Vulnerabilities
        vulnerabilities = profile.get('vulnerabilities', [])
        if vulnerabilities:
            md.append("## Vulnerabilities")
            md.append("")
            for vuln in vulnerabilities:
                md.append(f"### {vuln.get('type', 'Unknown')}")
                md.append(f"**Severity:** {vuln.get('severity', 'unknown').upper()}")
                md.append(f"**Description:** {vuln.get('description', 'N/A')}")
                md.append(f"**Recommendation:** {vuln.get('recommendation', 'N/A')}")
                md.append("")
        
        # Risk Factors
        risk_factors = risk.get('factors', [])
        if risk_factors:
            md.append("## Risk Factors")
            md.append("")
            for factor in risk_factors:
                md.append(f"- {factor}")
            md.append("")
        
        # Recommendations
        recommendations = risk.get('recommendations', [])
        if recommendations:
            md.append("## Recommendations")
            md.append("")
            for i, rec in enumerate(recommendations, 1):
                md.append(f"{i}. {rec}")
            md.append("")
        
        # Evidence
        md.append("## Evidence")
        md.append("")
        md.append(f"**Evidence Sealed:** {profile.get('evidence_sealed', False)}")
        evidence_files = profile.get('evidence_files', [])
        if evidence_files:
            md.append(f"**Evidence Files:** {len(evidence_files)}")
            for efile in evidence_files:
                md.append(f"- `{efile}`")
        md.append("")
        
        # Footer
        md.append("---")
        md.append(f"*Report generated by ForensicSense AI*")
        md.append(f"*{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write('\n'.join(md))
    
    def _generate_html(self, profile: Dict, output_path: Path):
        """Generate HTML report"""
        # First generate markdown, then convert to HTML
        md_path = output_path.with_suffix('.md')
        self._generate_markdown(profile, md_path)
        
        # Read markdown
        with open(md_path, 'r') as f:
            md_content = f.read()
        
        # Simple HTML wrapper
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Forensic Analysis Report - {profile.get('target')}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1, h2, h3 {{ color: #333; }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{ background-color: #f2f2f2; }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 5px;
            border-radius: 3px;
        }}
        .risk-critical {{ color: #d32f2f; font-weight: bold; }}
        .risk-high {{ color: #f57c00; font-weight: bold; }}
        .risk-medium {{ color: #fbc02d; font-weight: bold; }}
        .risk-low {{ color: #388e3c; font-weight: bold; }}
    </style>
</head>
<body>
    <pre style="white-space: pre-wrap;">{md_content}</pre>
</body>
</html>"""
        
        with open(output_path, 'w') as f:
            f.write(html)
        
        # Clean up temporary markdown file
        md_path.unlink()
    
    def _generate_pdf(self, profile: Dict, output_path: Path):
        """Generate PDF report using reportlab"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib import colors
            
            doc = SimpleDocTemplate(str(output_path), pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
            )
            story.append(Paragraph("Forensic Analysis Report", title_style))
            story.append(Spacer(1, 12))
            
            # Target Information
            story.append(Paragraph(f"<b>Target:</b> {profile.get('target')}", styles['Normal']))
            story.append(Paragraph(f"<b>Profile Depth:</b> {profile.get('profile_depth')}", styles['Normal']))
            story.append(Paragraph(f"<b>Completed:</b> {profile.get('completed_at')}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Risk Assessment
            story.append(Paragraph("Executive Summary", styles['Heading2']))
            risk = profile.get('risk_assessment', {})
            story.append(Paragraph(f"<b>Risk Level:</b> {risk.get('level', 'UNKNOWN')}", styles['Normal']))
            story.append(Paragraph(f"<b>Risk Score:</b> {risk.get('score', 0)}/100", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # More sections...
            story.append(Paragraph("Full report data available in JSON format.", styles['Normal']))
            
            # Build PDF
            doc.build(story)
            logger.info(f"PDF report generated: {output_path}")
            
        except ImportError:
            logger.warning("reportlab not installed - generating markdown instead")
            # Fallback to markdown
            md_path = output_path.with_suffix('.md')
            self._generate_markdown(profile, md_path)
            logger.info(f"Markdown report generated instead: {md_path}")
