import streamlit as st
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import requests
from PIL import Image
import io
import base64
import os
from groq import Groq
import json

class PresentationGenerator:
    def __init__(self):
        self.groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.templates = {
            "Modern Business": {
                "background_color": (45, 55, 72),
                "title_color": (255, 255, 255),
                "text_color": (226, 232, 240),
                "accent_color": (56, 178, 172)
            },
            "Clean Minimal": {
                "background_color": (255, 255, 255),
                "title_color": (45, 55, 72),
                "text_color": (74, 85, 104),
                "accent_color": (49, 130, 206)
            },
            "Corporate Blue": {
                "background_color": (23, 37, 84),
                "title_color": (255, 255, 255),
                "text_color": (203, 213, 224),
                "accent_color": (66, 153, 225)
            },
            "Warm Orange": {
                "background_color": (255, 248, 240),
                "title_color": (194, 65, 12),
                "text_color": (124, 45, 18),
                "accent_color": (251, 146, 60)
            },
            "Professional Green": {
                "background_color": (240, 253, 244),
                "title_color": (22, 101, 52),
                "text_color": (20, 83, 45),
                "accent_color": (72, 187, 120)
            }
        }
    
    def create_presentation_from_analysis(self, analysis_data, template_name="Modern Business"):
        """Create a presentation from analysis data"""
        prs = Presentation()
        template = self.templates[template_name]
        
        # Title slide
        title_slide = prs.slides.add_slide(prs.slide_layouts[0])
        title = title_slide.shapes.title
        subtitle = title_slide.placeholders[1]
        
        if title and hasattr(title, 'text_frame'):
            title.text = "Data Analysis Results"
        if subtitle and hasattr(subtitle, 'text_frame'):
            subtitle.text = "AI-Powered Business Intelligence Report"
        
        self._apply_template_styling(title_slide, template)
        
        # Executive Summary slide
        if analysis_data.get('summary'):
            summary_slide = prs.slides.add_slide(prs.slide_layouts[1])
            title = summary_slide.shapes.title
            content = summary_slide.placeholders[1]
            
            if title and hasattr(title, 'text_frame'):
                title.text = "Executive Summary"
            if content and hasattr(content, 'text_frame'):
                content.text = analysis_data['summary']
            
            self._apply_template_styling(summary_slide, template)
        
        # Key Insights slide
        if analysis_data.get('insights'):
            insights_slide = prs.slides.add_slide(prs.slide_layouts[1])
            title = insights_slide.shapes.title
            content = insights_slide.placeholders[1]
            
            if title and hasattr(title, 'text_frame'):
                title.text = "Key Insights"
            if content and hasattr(content, 'text_frame'):
                insights_text = "\n".join([f"• {insight}" for insight in analysis_data['insights']])
                content.text = insights_text
            
            self._apply_template_styling(insights_slide, template)
        
        # Recommendations slide
        if analysis_data.get('recommendations'):
            rec_slide = prs.slides.add_slide(prs.slide_layouts[1])
            title = rec_slide.shapes.title
            content = rec_slide.placeholders[1]
            
            if title and hasattr(title, 'text_frame'):
                title.text = "Recommendations"
            if content and hasattr(content, 'text_frame'):
                rec_text = "\n".join([f"• {rec}" for rec in analysis_data['recommendations']])
                content.text = rec_text
            
            self._apply_template_styling(rec_slide, template)
        
        return prs
    
    def _apply_template_styling(self, slide, template):
        """Apply template styling to slide"""
        # Set background color
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(*template["background_color"])
        
        # Style title and content
        for shape in slide.shapes:
            if hasattr(shape, "text_frame"):
                text_frame = shape.text_frame
                for paragraph in text_frame.paragraphs:
                    for run in paragraph.runs:
                        if shape == slide.shapes.title:
                            run.font.color.rgb = RGBColor(*template["title_color"])
                            run.font.size = Pt(44)
                            run.font.bold = True
                        else:
                            run.font.color.rgb = RGBColor(*template["text_color"])
                            run.font.size = Pt(24)
    
    def add_image_to_slide(self, prs, slide_index, image_path, left=Inches(1), top=Inches(2), width=Inches(8)):
        """Add an image to a specific slide"""
        if slide_index < len(prs.slides):
            slide = prs.slides[slide_index]
            slide.shapes.add_picture(image_path, left, top, width=width)
            return True
        return False
    
    def generate_image_description(self, slide_content, context="business presentation"):
        """Generate image description using Groq"""
        try:
            prompt = f"""Based on this slide content: "{slide_content}"
            
            Generate a professional image description for a {context} that would complement this content.
            The description should be suitable for AI image generation and focus on:
            - Professional business imagery
            - Clean, modern aesthetic
            - Relevant visual metaphors
            - Appropriate colors and composition
            
            Respond with only the image description, no additional text."""
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else f"Professional business illustration related to: {slide_content[:100]}"
        except Exception as e:
            return f"Professional business illustration related to: {slide_content[:100]}"
    
    def create_custom_slide(self, prs, title, content, template_name="Modern Business"):
        """Create a custom slide with title and content"""
        template = self.templates[template_name]
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        
        slide_title = slide.shapes.title
        slide_content = slide.placeholders[1]
        
        if slide_title and hasattr(slide_title, 'text_frame'):
            slide_title.text = title
        if slide_content and hasattr(slide_content, 'text_frame'):
            slide_content.text = content
        
        self._apply_template_styling(slide, template)
        return slide
    
    def save_presentation(self, prs, filename):
        """Save presentation to file"""
        filepath = f"presentations/{filename}"
        os.makedirs("presentations", exist_ok=True)
        prs.save(filepath)
        return filepath
    
    def get_slide_preview_text(self, prs):
        """Get text preview of all slides"""
        slides_preview = []
        for i, slide in enumerate(prs.slides):
            slide_text = []
            for shape in slide.shapes:
                if hasattr(shape, "text_frame") and shape.text_frame.text:
                    slide_text.append(shape.text_frame.text)
            
            slides_preview.append({
                "slide_number": i + 1,
                "content": "\n".join(slide_text)
            })
        
        return slides_preview

class ImageGenerator:
    def __init__(self):
        self.groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    def generate_svg_image(self, prompt):
        """Generate SVG image description using Groq for business presentations"""
        try:
            svg_prompt = f"""Create a simple, professional SVG image for: {prompt}
            
            Generate SVG code that creates a clean, business-appropriate illustration.
            Requirements:
            - Use professional colors (blues, grays, greens)
            - Simple geometric shapes and icons
            - Minimal design suitable for presentations
            - Size: 400x300 viewBox
            - Include relevant business icons or charts
            
            Respond with only the SVG code, starting with <svg> and ending with </svg>."""
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": svg_prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            svg_content = content.strip() if content else ""
            
            # Extract SVG if wrapped in code blocks
            if "```" in svg_content:
                svg_content = svg_content.split("```")[1]
                if svg_content.startswith("svg"):
                    svg_content = svg_content[3:]
            
            # Ensure it starts with <svg
            if not svg_content.strip().startswith("<svg"):
                return self._create_fallback_svg(prompt)
            
            return svg_content
            
        except Exception as e:
            return self._create_fallback_svg(prompt)
    
    def _create_fallback_svg(self, prompt):
        """Create a simple fallback SVG"""
        return f'''<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="300" fill="#f8f9fa" stroke="#dee2e6" stroke-width="2"/>
            <circle cx="200" cy="150" r="60" fill="#007bff" opacity="0.8"/>
            <text x="200" y="220" text-anchor="middle" font-family="Arial" font-size="16" fill="#495057">
                {prompt[:30]}...
            </text>
        </svg>'''
    
    def save_svg_as_image(self, svg_content, filename):
        """Save SVG content as image file"""
        os.makedirs("generated_images", exist_ok=True)
        filepath = f"generated_images/{filename}.svg"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        return filepath