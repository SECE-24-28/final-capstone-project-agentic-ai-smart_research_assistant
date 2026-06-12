from sqlalchemy.orm import Session
from ..models import Paper, Summary, Comparison, FinalReport

class ReportService:
    def __init__(self, session: Session):
        self.session = session

    def generate_final_report(self, topic: str, paper_ids: list[int], comparison_id: int | None) -> FinalReport:
        papers = self.session.query(Paper).filter(Paper.id.in_(paper_ids)).all()
        
        comparison = None
        if comparison_id:
            comparison = self.session.query(Comparison).filter(Comparison.id == comparison_id).first()
            

        report_content = [
            f"# Complete Research Report: {topic}\n",
            "## 1. Selected Papers\n"
        ]
        
        for paper in papers:
            report_content.append(f"### {paper.title}")
            report_content.append(f"**Authors:** {paper.authors or 'N/A'}")
            report_content.append(f"**Year:** {paper.year or 'N/A'}")
            report_content.append(f"**Journal/Source:** {paper.journal or paper.source or 'N/A'}")
            
            if paper.summaries:
                s = paper.summaries[0]
                report_content.append("\n#### Structured Summary")
                report_content.append(f"- **Objective:** {s.objective or 'Not provided'}")
                report_content.append(f"- **Methodology:** {s.methodology or 'Not provided'}")
                report_content.append(f"- **Findings:** {s.findings or 'Not provided'}")
                report_content.append(f"- **Limitations:** {s.limitations or 'Not provided'}")
            report_content.append("\n---\n")

        if comparison:
            report_content.append("## 2. Comparative Analysis\n")
            report_content.append(comparison.result)
            report_content.append("\n---\n")


        final_content = "\n".join(report_content)

        final_report = FinalReport(
            topic=topic,
            paper_ids=",".join(map(str, paper_ids)),
            content=final_content
        )
        self.session.add(final_report)
        self.session.commit()
        self.session.refresh(final_report)
        
        return final_report

report_service = ReportService
