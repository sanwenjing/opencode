#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Professional PowerPoint Presentation Standards Validator
Validates PowerPoint presentations against professional design standards
"""

from pptx import Presentation
import sys
import argparse
from typing import Dict, List
from ppt_generator_pro import PresentationStandards


class PresentationValidator:
    """Validator for professional presentation standards"""
    
    def __init__(self):
        self.standards = PresentationStandards()
        self.validation_results = []
    
    def validate_file(self, pptx_path: str) -> Dict[str, any]:
        """Validate a PowerPoint file against professional standards"""
        try:
            presentation = Presentation(pptx_path)
            return self.validate_presentation(presentation)
        except Exception as e:
            return {"error": f"Failed to open presentation: {e}"}
    
    def validate_presentation(self, presentation: Presentation) -> Dict[str, any]:
        """Validate presentation content and structure"""
        results = {
            "file_info": {},
            "slide_validations": [],
            "overall_score": 0,
            "recommendations": []
        }
        
        # Basic file info
        results["file_info"] = {
            "slide_count": len(presentation.slides),
            "layout": "16:9" if self._is_16_9(presentation) else "Unknown"
        }
        
        # Validate each slide
        for i, slide in enumerate(presentation.slides):
            slide_validation = self.validate_slide(slide, i)
            results["slide_validations"].append(slide_validation)
        
        # Calculate overall score
        scores = [sv["score"] for sv in results["slide_validations"] if "score" in sv]
        if scores:
            results["overall_score"] = sum(scores) / len(scores)
        
        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results["slide_validations"])
        
        return results
    
    def validate_slide(self, slide, slide_index: int) -> Dict[str, any]:
        """Validate individual slide"""
        validation = {
            "slide_number": slide_index + 1,
            "issues": [],
            "score": 0,
            "max_points": 100
        }
        
        # Check for title
        if not slide.shapes.title:
            validation["issues"].append({
                "type": "missing_title",
                "severity": "error",
                "message": "Slide has no title"
            })
            validation["score"] -= 20
        else:
            # Check title formatting
            title_issues = self._validate_title_formatting(slide.shapes.title)
            validation["issues"].extend(title_issues)
            validation["score"] -= len(title_issues) * 5
        
        # Check content density
        content_issues = self._validate_content_density(slide)
        validation["issues"].extend(content_issues)
        validation["score"] -= len(content_issues) * 3
        
        # Check typography
        typo_issues = self._validate_typography(slide)
        validation["issues"].extend(typo_issues)
        validation["score"] -= len(typo_issues) * 2
        
        # Ensure score doesn't go below 0
        validation["score"] = max(0, validation["score"])
        
        return validation
    
    def _validate_title_formatting(self, title_shape) -> List[Dict]:
        """Validate title formatting against standards"""
        issues = []
        
        if not title_shape.text_frame.paragraphs:
            issues.append({
                "type": "empty_title",
                "severity": "warning",
                "message": "Title appears to be empty"
            })
            return issues
        
        for paragraph in title_shape.text_frame.paragraphs:
            # Check font size
            if hasattr(paragraph.font, 'size') and paragraph.font.size:
                font_size = paragraph.font.size.pt
                if font_size < self.standards.FONT_SIZE_SUBTITLE:
                    issues.append({
                        "type": "title_font_too_small",
                        "severity": "warning",
                        "message": f"Title font size {font_size}pt is below recommended {self.standards.FONT_SIZE_SUBTITLE}pt"
                    })
        
        return issues
    
    def _validate_content_density(self, slide) -> List[Dict]:
        """Validate content density and readability"""
        issues = []
        text_content = ""
        
        # Extract all text from slide
        for shape in slide.shapes:
            if hasattr(shape, 'text_frame') and shape.text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    if paragraph.text:
                        text_content += paragraph.text + " "
        
        # Check line count
        lines = [line.strip() for line in text_content.split('\n') if line.strip()]
        if len(lines) > self.standards.MAX_LINES_PER_SLIDE:
            issues.append({
                "type": "content_too_dense",
                "severity": "warning",
                "message": f"Slide has {len(lines)} text lines (recommended max: {self.standards.MAX_LINES_PER_SLIDE})"
            })
        
        # Check character count per line
        for i, line in enumerate(lines):
            if len(line) > self.standards.MAX_CHARS_PER_LINE_ZH:
                issues.append({
                    "type": "line_too_long",
                    "severity": "info",
                    "message": f"Line {i+1}: {len(line)} characters (recommended max: {self.standards.MAX_CHARS_PER_LINE_ZH})"
                })
        
        return issues
    
    def _validate_typography(self, slide) -> List[Dict]:
        """Validate typography standards"""
        issues = []
        
        for shape in slide.shapes:
            if hasattr(shape, 'text_frame') and shape.text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    # Check minimum font size
                    if hasattr(paragraph.font, 'size') and paragraph.font.size:
                        font_size = paragraph.font.size.pt
                        if font_size < self.standards.FONT_SIZE_MIN:
                            issues.append({
                                "type": "font_too_small",
                                "severity": "error",
                                "message": f"Font size {font_size}pt is below minimum {self.standards.FONT_SIZE_MIN}pt"
                            })
                    
                    # Check for font consistency (simplified check)
                    if hasattr(paragraph.font, 'name') and paragraph.font.name:
                        font_name = paragraph.font.name.lower()
                        if any(unwanted in font_name for unwanted in ['comic sans', 'papyrus', 'brush script']):
                            issues.append({
                                "type": "unprofessional_font",
                                "severity": "warning",
                                "message": f"Font '{paragraph.font.name}' may not be suitable for professional presentations"
                            })
        
        return issues
    
    def _is_16_9(self, presentation) -> bool:
        """Check if presentation uses 16:9 layout"""
        # This is a simplified check - in reality would need to examine slide dimensions
        return True  # Assuming modern presentations use 16:9
    
    def _generate_recommendations(self, slide_validations: List[Dict]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Collect all issue types
        all_issues = []
        for sv in slide_validations:
            all_issues.extend([issue["type"] for issue in sv["issues"]])
        
        # Generate recommendations based on common issues
        if "missing_title" in all_issues:
            recommendations.append("Add descriptive titles to all slides for better navigation")
        
        if "font_too_small" in all_issues:
            recommendations.append("Increase font sizes to meet minimum readability standards (12pt minimum, 18pt recommended for body text)")
        
        if "content_too_dense" in all_issues:
            recommendations.append("Reduce content density or split content across multiple slides for better readability")
        
        if "line_too_long" in all_issues:
            recommendations.append("Break long lines into shorter ones for improved readability")
        
        if "unprofessional_font" in all_issues:
            recommendations.append("Use professional fonts like Arial, Calibri, or Microsoft YaHei for presentations")
        
        return recommendations


def print_validation_report(results: Dict[str, any]) -> None:
    """Print formatted validation report"""
    print("=" * 60)
    print("📋 PROFESSIONAL PRESENTATION VALIDATION REPORT")
    print("=" * 60)
    
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return
    
    # File info
    info = results["file_info"]
    print(f"📊 File Information:")
    print(f"   • Slide Count: {info['slide_count']}")
    print(f"   • Layout: {info['layout']}")
    print(f"   • Overall Score: {results['overall_score']:.1f}/100")
    print()
    
    # Slide-by-slide validation
    print("🔍 Slide Validation Results:")
    for sv in results["slide_validations"]:
        print(f"   Slide {sv['slide_number']}: Score {sv['score']}/{sv['max_points']}")
        if sv["issues"]:
            for issue in sv["issues"]:
                severity_icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(issue["severity"], "•")
                print(f"     {severity_icon} {issue['message']}")
        else:
            print("     ✅ No issues found")
    
    # Recommendations
    if results["recommendations"]:
        print()
        print("💡 Recommendations for Improvement:")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"   {i}. {rec}")
    else:
        print()
        print("🎉 Excellent! Your presentation meets professional standards.")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Validate PowerPoint presentations against professional standards")
    parser.add_argument("file", help="PowerPoint file to validate")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        return 1
    
    validator = PresentationValidator()
    results = validator.validate_file(args.file)
    print_validation_report(results)
    
    return 0


if __name__ == "__main__":
    import os
    exit(main())