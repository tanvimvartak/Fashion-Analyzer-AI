"""
Smart Response Generator for Fashion Analyzer
Uses advanced NLP techniques to generate contextual, intelligent responses
"""

import re
from typing import Dict, List

class SmartResponseGenerator:
    """
    Generates intelligent, context-aware fashion advice responses
    """
    
    def __init__(self):
        # Color pairing knowledge base
        self.color_pairings = {
            'pink': {
                'best_matches': ['white', 'black', 'gray', 'navy', 'denim', 'beige', 'cream'],
                'avoid': ['red', 'orange'],
                'style_tips': 'Pink is versatile! Baby pink works with neutrals, hot pink makes a statement with black or white.'
            },
            'red': {
                'best_matches': ['black', 'white', 'navy', 'denim', 'beige', 'gray'],
                'avoid': ['pink', 'orange', 'purple'],
                'style_tips': 'Red is bold! Pair with neutrals to let it shine, or go monochrome for drama.'
            },
            'maroon': {
                'best_matches': ['white', 'cream', 'beige', 'gold', 'black', 'gray', 'navy'],
                'avoid': ['bright red', 'orange', 'bright pink'],
                'style_tips': 'Maroon is rich and sophisticated! Perfect for fall/winter. Pairs beautifully with neutrals and metallics.'
            },
            'burgundy': {
                'best_matches': ['white', 'cream', 'beige', 'gold', 'black', 'gray', 'navy'],
                'avoid': ['bright red', 'orange', 'bright pink'],
                'style_tips': 'Burgundy is elegant and luxurious! Great for formal occasions. Works wonderfully with gold accessories.'
            },
            'wine': {
                'best_matches': ['white', 'cream', 'beige', 'gold', 'black', 'gray'],
                'avoid': ['bright colors'],
                'style_tips': 'Wine color is classy and timeless! Perfect for evening wear and special occasions.'
            },
            'blue': {
                'best_matches': ['white', 'beige', 'brown', 'gray', 'yellow', 'pink'],
                'avoid': ['black (unless navy)'],
                'style_tips': 'Blue is universally flattering. Navy works like a neutral, lighter blues are fresh and casual.'
            },
            'black': {
                'best_matches': ['literally everything', 'white', 'red', 'pink', 'gold', 'silver'],
                'avoid': [],
                'style_tips': 'Black is the ultimate neutral. Goes with everything and always looks chic!'
            },
            'white': {
                'best_matches': ['everything', 'denim', 'pastels', 'bright colors'],
                'avoid': [],
                'style_tips': 'White is fresh and clean. Perfect base for any color combination!'
            },
            'green': {
                'best_matches': ['white', 'beige', 'brown', 'navy', 'denim'],
                'avoid': ['blue', 'purple'],
                'style_tips': 'Green is earthy and fresh. Olive green is very versatile, emerald is luxurious.'
            },
            'yellow': {
                'best_matches': ['white', 'gray', 'navy', 'denim', 'black'],
                'avoid': ['green', 'orange'],
                'style_tips': 'Yellow is cheerful! Mustard yellow is trendy, bright yellow makes a statement.'
            },
            'purple': {
                'best_matches': ['white', 'gray', 'black', 'beige', 'silver'],
                'avoid': ['red', 'orange'],
                'style_tips': 'Purple is regal! Lavender is soft and feminine, deep purple is sophisticated.'
            },
            'brown': {
                'best_matches': ['white', 'cream', 'beige', 'blue', 'green', 'orange'],
                'avoid': ['black', 'gray'],
                'style_tips': 'Brown is warm and earthy. Great for casual, natural looks.'
            },
            'gray': {
                'best_matches': ['everything', 'pink', 'yellow', 'blue', 'white'],
                'avoid': [],
                'style_tips': 'Gray is a sophisticated neutral. Works with both warm and cool colors!'
            },
            'orange': {
                'best_matches': ['white', 'denim', 'navy', 'brown', 'beige'],
                'avoid': ['red', 'pink', 'purple'],
                'style_tips': 'Orange is energetic! Burnt orange is trendy, bright orange is bold.'
            },
            'navy': {
                'best_matches': ['white', 'cream', 'beige', 'red', 'pink', 'gold'],
                'avoid': ['black'],
                'style_tips': 'Navy is a sophisticated neutral! Works like black but softer. Perfect for professional looks.'
            },
            'beige': {
                'best_matches': ['white', 'brown', 'navy', 'black', 'pastels'],
                'avoid': [],
                'style_tips': 'Beige is elegant and neutral! Creates a soft, sophisticated look. Great base color.'
            },
            'cream': {
                'best_matches': ['brown', 'beige', 'navy', 'burgundy', 'gold'],
                'avoid': ['white (too similar)'],
                'style_tips': 'Cream is softer than white! Perfect for creating elegant, warm looks.'
            },
            'gold': {
                'best_matches': ['black', 'white', 'navy', 'burgundy', 'green'],
                'avoid': ['silver'],
                'style_tips': 'Gold is luxurious! Great for accessories and evening wear. Adds instant glamour.'
            },
            'silver': {
                'best_matches': ['black', 'white', 'gray', 'blue', 'purple'],
                'avoid': ['gold'],
                'style_tips': 'Silver is sleek and modern! Perfect for cool-toned outfits and contemporary looks.'
            },
            'turquoise': {
                'best_matches': ['white', 'beige', 'brown', 'navy', 'coral'],
                'avoid': ['green', 'blue'],
                'style_tips': 'Turquoise is vibrant and fresh! Perfect for summer and beach looks.'
            },
            'lavender': {
                'best_matches': ['white', 'gray', 'silver', 'navy', 'cream'],
                'avoid': ['orange', 'red'],
                'style_tips': 'Lavender is soft and feminine! Creates dreamy, romantic looks.'
            },
            'magenta': {
                'best_matches': ['black', 'white', 'navy', 'gray'],
                'avoid': ['red', 'orange'],
                'style_tips': 'Magenta is bold and vibrant! Makes a strong statement. Pair with neutrals.'
            }
        }
        
        # Clothing item specific advice
        self.clothing_advice = {
            'jeans': {
                'colors': ['any color works', 'especially white', 'black', 'pastels', 'bright colors'],
                'style': 'Denim is the ultimate neutral bottom. Dress up with heels or down with sneakers.',
                'occasions': ['casual', 'date', 'shopping', 'brunch']
            },
            'skirt': {
                'colors': ['depends on skirt color', 'neutrals are safe', 'complementary colors'],
                'style': 'Balance proportions - fitted top with flowy skirt, or vice versa.',
                'occasions': ['work', 'date', 'party', 'casual']
            },
            'dress': {
                'colors': ['accessories should complement', 'shoes can match or contrast'],
                'style': 'A dress is a complete outfit! Just add shoes and accessories.',
                'occasions': ['any occasion depending on style']
            },
            'pants': {
                'colors': ['neutral pants = colorful top', 'colored pants = neutral top'],
                'style': 'Tailored pants look professional, casual pants are comfortable.',
                'occasions': ['work', 'casual', 'formal']
            },
            'top': {
                'colors': ['match with bottom color', 'or create contrast'],
                'style': 'Tucked in for polished look, untucked for casual vibe.',
                'occasions': ['versatile for any occasion']
            },
            'shirt': {
                'colors': ['white is classic', 'pastels are soft', 'patterns add interest'],
                'style': 'Button-ups are versatile - formal or casual depending on styling.',
                'occasions': ['work', 'casual', 'date']
            },
            'blouse': {
                'colors': ['feminine colors like pastels', 'or bold jewel tones'],
                'style': 'Blouses are elegant and feminine. Great for work or dressy occasions.',
                'occasions': ['work', 'formal', 'date']
            }
        }
    
    def generate_intelligent_response(self, message: str, nlp_context: Dict, dataset_insights: Dict, image_colors: List[str]) -> str:
        """
        Generate a smart, contextual response based on the actual question
        """
        message_lower = message.lower()
        entities = nlp_context.get('entities', {})
        intent = nlp_context.get('intent', 'general_fashion')
        
        # Extract the actual question being asked
        colors_mentioned = entities.get('colors', [])
        clothing_mentioned = entities.get('clothing_types', [])
        occasions_mentioned = entities.get('occasions', [])
        
        # If image colors detected, prioritize image analysis
        if image_colors:
            response = self._handle_image_analysis(
                image_colors, message_lower, dataset_insights, colors_mentioned, clothing_mentioned
            )
        
        # Handle specific color + clothing combinations
        elif colors_mentioned and clothing_mentioned:
            response = self._handle_color_clothing_question(
                colors_mentioned, clothing_mentioned, message_lower, dataset_insights
            )
        
        # Handle "what to wear with" questions
        elif any(phrase in message_lower for phrase in ['what to wear', 'what should i wear', 'what can i wear', 'what goes with', 'what matches']):
            response = self._handle_what_to_wear_question(
                message_lower, colors_mentioned, clothing_mentioned, dataset_insights
            )
        
        # Handle color matching questions
        elif any(phrase in message_lower for phrase in ['color', 'match', 'goes with', 'pair with']):
            response = self._handle_color_matching_question(
                colors_mentioned, clothing_mentioned, message_lower, dataset_insights
            )
        
        # Handle occasion-based questions
        elif occasions_mentioned:
            response = self._handle_occasion_question(
                occasions_mentioned, colors_mentioned, clothing_mentioned, dataset_insights
            )
        
        # Handle "don't know" or uncertainty
        elif any(phrase in message_lower for phrase in ["don't know", "not sure", "confused", "help"]):
            response = self._handle_uncertainty_question(
                message_lower, colors_mentioned, clothing_mentioned, dataset_insights
            )
        
        # Default intelligent response
        else:
            response = self._generate_default_intelligent_response(
                message, nlp_context, dataset_insights
            )
        
        # Add dataset insights footer
        response += self._add_dataset_footer(dataset_insights)
        
        return response
    
    def _handle_image_analysis(self, image_colors: List[str], message: str, dataset_insights: Dict, colors_mentioned: List[str], clothing_mentioned: List[str]) -> str:
        """Handle image analysis with detected colors"""
        response = "**✨ Fashion Analysis of Your Image! ✨**\n\n"
        
        # Get unique colors from image
        detected_colors = list(dict.fromkeys(image_colors))  # Preserve order, remove duplicates
        
        # Filter out background colors to find the main garment color
        clothing_colors = [c for c in detected_colors if c.lower() not in ['white', 'black', 'gray']]
        
        # Primary color is the first non-background color, or first color if all are background
        primary_color = clothing_colors[0] if clothing_colors else detected_colors[0] if detected_colors else None
        
        response += f"**🎨 Colors Detected in Your Image:**\n"
        response += f"**Main Color:** {primary_color.title()} 👗\n"
        if len(detected_colors) > 1:
            other_colors = [c for c in detected_colors if c != primary_color]
            if other_colors:
                response += f"Also detected: {', '.join([c.title() for c in other_colors[:2]])}\n"
        response += "\n"
        
        # Analyze the primary color
        if primary_color and primary_color.lower() in self.color_pairings:
            color_info = self.color_pairings[primary_color.lower()]
            
            response += f"**💕 Styling Your {primary_color.title()} Item:**\n\n"
            
            response += f"**What Works Beautifully:**\n"
            for match in color_info['best_matches'][:6]:
                response += f"✓ {match.title()}\n"
            response += "\n"
            
            if color_info['avoid']:
                response += f"**What to Avoid:**\n"
                for avoid in color_info['avoid']:
                    response += f"✗ {avoid.title()}\n"
                response += "\n"
            
            response += f"**💡 Style Tip:** {color_info['style_tips']}\n\n"
        
        # Provide complete outfit suggestions based on detected colors
        response += "**👗 How to Style This Piece:**\n\n"
        
        if primary_color:
            # Determine the type of garment from the message or image context
            is_dress = any(word in message.lower() for word in ['dress', 'gown', 'frock', 'one piece', 'onepiece', 'one-piece'])
            is_top = any(word in message.lower() for word in ['top', 'shirt', 'blouse', 't-shirt', 'tshirt', 'sweater', 'jacket'])
            is_bottom = any(word in message.lower() for word in ['jeans', 'pants', 'skirt', 'shorts', 'bottom', 'trousers'])
            
            # Check if similar items in dataset are dresses
            if dataset_insights.get('similar_outfits'):
                similar_names = ' '.join([outfit['filename'].lower() for outfit in dataset_insights['similar_outfits'][:3]])
                if 'dress' in similar_names and not is_top and not is_bottom:
                    is_dress = True
            
            if is_dress:
                # It's a dress - give complete dress styling advice
                response += f"**Your {primary_color.title()} Dress - Complete Look Ideas:**\n\n"
                response += f"**Casual Day Look:**\n"
                response += f"• {primary_color.title()} dress + white sneakers + denim jacket\n"
                response += f"• Add: crossbody bag, sunglasses\n\n"
                
                response += f"**Office/Work Look:**\n"
                response += f"• {primary_color.title()} dress + nude heels + blazer\n"
                response += f"• Add: structured tote, simple jewelry\n\n"
                
                response += f"**Date Night/Evening:**\n"
                response += f"• {primary_color.title()} dress + black heels + clutch\n"
                response += f"• Add: statement earrings, bold lip\n\n"
                
                response += f"**Weekend Brunch:**\n"
                response += f"• {primary_color.title()} dress + sandals + cardigan\n"
                response += f"• Add: straw bag, delicate necklace\n\n"
                
            elif is_top:
                # It's a top
                response += f"**Your {primary_color.title()} Top - Pairing Ideas:**\n"
                response += f"1. {primary_color.title()} top + white jeans + white sneakers (fresh & casual)\n"
                response += f"2. {primary_color.title()} top + black pants + heels (sleek & elegant)\n"
                response += f"3. {primary_color.title()} top + denim skirt + sandals (cute & fun)\n"
                response += f"4. {primary_color.title()} top + beige trousers + loafers (sophisticated)\n\n"
                
            elif is_bottom:
                # It's a bottom
                response += f"**Your {primary_color.title()} Bottom - Pairing Ideas:**\n"
                response += f"1. White blouse + {primary_color} bottom + nude heels (classic)\n"
                response += f"2. Black top + {primary_color} bottom + black boots (edgy)\n"
                response += f"3. Cream sweater + {primary_color} bottom + flats (cozy)\n"
                response += f"4. Striped tee + {primary_color} bottom + sneakers (casual)\n\n"
                
            else:
                # Unknown - assume it's a dress or complete outfit
                response += f"**Your {primary_color.title()} Piece - Styling Ideas:**\n\n"
                response += f"**If it's a Dress/Complete Outfit:**\n"
                response += f"• Casual: Add white sneakers + denim jacket\n"
                response += f"• Dressy: Add heels + statement jewelry\n"
                response += f"• Work: Add blazer + closed-toe heels\n\n"
                
                response += f"**If it's a Separates:**\n"
                response += f"• Pair with neutrals (white, black, beige)\n"
                response += f"• Add complementary accessories\n"
                response += f"• Keep the rest simple to let the {primary_color} shine\n\n"
        
        # Add accessory suggestions
        response += "**👠 Complete the Look:**\n"
        response += "• **Shoes:** White sneakers (casual) or black heels (dressy)\n"
        response += "• **Bag:** Neutral color (black, brown, or beige)\n"
        response += "• **Jewelry:** Keep it simple - small earrings, delicate necklace\n"
        response += "• **Watch/Bracelet:** Gold or silver depending on your skin tone\n\n"
        
        # Add occasion suggestions based on color and garment type
        response += "**📅 Perfect Occasions:**\n"
        
        # Determine garment type again for occasion suggestions
        is_dress = any(word in message.lower() for word in ['dress', 'gown', 'frock', 'one piece', 'onepiece', 'one-piece'])
        if dataset_insights.get('similar_outfits'):
            similar_names = ' '.join([outfit['filename'].lower() for outfit in dataset_insights['similar_outfits'][:3]])
            if 'dress' in similar_names:
                is_dress = True
        
        if primary_color and primary_color.lower() in ['black', 'navy', 'gray', 'white']:
            if is_dress:
                response += "• Work/Office meetings ✓\n• Business lunches ✓\n• Formal events ✓\n• Date nights ✓\n• Versatile for any occasion!\n"
            else:
                response += "• Work/Office ✓\n• Casual outings ✓\n• Date night ✓\n• Almost any occasion!\n"
        elif primary_color and primary_color.lower() in ['red', 'maroon', 'burgundy', 'wine']:
            if is_dress:
                response += "• Date nights ✓\n• Cocktail parties ✓\n• Holiday events ✓\n• Romantic dinners ✓\n• Special occasions!\n"
            else:
                response += "• Date night ✓\n• Party/Events ✓\n• Confidence boost days!\n"
        elif primary_color and primary_color.lower() in ['pink', 'purple', 'lavender']:
            if is_dress:
                response += "• Brunch dates ✓\n• Garden parties ✓\n• Spring/Summer events ✓\n• Girls' day out ✓\n"
            else:
                response += "• Date night ✓\n• Party/Events ✓\n• Girls' night out ✓\n"
        else:
            if is_dress:
                response += "• Weekend brunches ✓\n• Casual dates ✓\n• Shopping trips ✓\n• Day events ✓\n• Everyday wear!\n"
            else:
                response += "• Casual hangouts ✓\n• Weekend brunch ✓\n• Shopping trips ✓\n• Fun outings!\n"
        
        response += "\n"
        
        # Add similar items from dataset if available
        if dataset_insights.get('similar_outfits'):
            response += "**💎 Similar Styles in Our Collection:**\n"
            for i, outfit in enumerate(dataset_insights['similar_outfits'][:3], 1):
                outfit_name = outfit['filename'].replace('.jpg', '').replace('_', ' ').title()
                response += f"{i}. {outfit_name}\n"
            response += "\n"
        
        # Add confidence boost
        response += "**✨ Final Thoughts:**\n"
        response += f"This {primary_color} piece is versatile and stylish! The key is pairing it with neutrals "
        response += "to let the color shine, or going bold with complementary colors. Most importantly, "
        response += "wear it with confidence - that's your best accessory! 💕\n"
        
        return response
    
    def _handle_color_clothing_question(self, colors: List[str], clothing: List[str], message: str, dataset_insights: Dict) -> str:
        """Handle questions about specific color + clothing combinations"""
        response = "**✨ Perfect! Let me help you style that! ✨**\n\n"
        
        primary_color = colors[0] if colors else None
        primary_clothing = clothing[0] if clothing else None
        
        if primary_color and primary_clothing:
            response += f"**Your {primary_color.title()} {primary_clothing.title()} - Complete Styling Guide:**\n\n"
            
            # Get color pairing advice
            if primary_color in self.color_pairings:
                color_info = self.color_pairings[primary_color]
                response += f"**🎨 Best Color Matches:**\n"
                for match in color_info['best_matches'][:6]:
                    response += f"✓ {match.title()}\n"
                
                if color_info['avoid']:
                    response += f"\n**What to Avoid:**\n"
                    for avoid in color_info['avoid'][:3]:
                        response += f"✗ {avoid.title()}\n"
                
                response += f"\n💡 **Style Tip:** {color_info['style_tips']}\n\n"
            
            # Complete outfit ideas based on clothing type
            response += f"**👗 Complete Outfit Ideas:**\n\n"
            
            if primary_clothing in ['top', 'shirt', 'blouse', 'sweater']:
                response += f"**Casual Day Look:**\n"
                response += f"• {primary_color.title()} {primary_clothing} + white jeans + white sneakers\n"
                response += f"• Add: denim jacket, crossbody bag\n\n"
                
                response += f"**Office/Work Look:**\n"
                response += f"• {primary_color.title()} {primary_clothing} + black trousers + heels\n"
                response += f"• Add: blazer, structured tote\n\n"
                
                response += f"**Date Night:**\n"
                response += f"• {primary_color.title()} {primary_clothing} + leather pants + heels\n"
                response += f"• Add: statement earrings, clutch\n\n"
                
                response += f"**Weekend Casual:**\n"
                response += f"• {primary_color.title()} {primary_clothing} + denim skirt + sandals\n"
                response += f"• Add: sunglasses, tote bag\n\n"
                
            elif primary_clothing in ['jeans', 'pants', 'skirt', 'shorts']:
                response += f"**Casual Day Look:**\n"
                response += f"• White t-shirt + {primary_color} {primary_clothing} + sneakers\n"
                response += f"• Add: denim jacket, backpack\n\n"
                
                response += f"**Office/Work Look:**\n"
                response += f"• Blouse + {primary_color} {primary_clothing} + heels\n"
                response += f"• Add: blazer, work bag\n\n"
                
                response += f"**Date Night:**\n"
                response += f"• Fitted top + {primary_color} {primary_clothing} + heels\n"
                response += f"• Add: statement jewelry, clutch\n\n"
                
                response += f"**Weekend Brunch:**\n"
                response += f"• Sweater + {primary_color} {primary_clothing} + flats\n"
                response += f"• Add: cardigan, tote bag\n\n"
            
            else:
                response += f"**Style It With:**\n"
                response += f"• Neutral colors (white, black, beige)\n"
                response += f"• Complementary accessories\n"
                response += f"• Simple shoes to let the piece shine\n\n"
            
            # Add accessories section
            response += f"**👠 Complete the Look:**\n"
            response += f"• **Shoes:** White sneakers (casual) or black heels (dressy)\n"
            response += f"• **Bag:** Neutral color (black, brown, beige)\n"
            response += f"• **Jewelry:** Keep it simple - small earrings, delicate necklace\n"
            response += f"• **Watch/Bracelet:** Gold or silver depending on your style\n\n"
            
            # Add occasion suggestions
            response += f"**📅 Perfect For:**\n"
            if primary_color in ['black', 'white', 'navy', 'gray']:
                response += f"• Work/Office ✓\n• Casual outings ✓\n• Date nights ✓\n• Almost any occasion!\n\n"
            elif primary_color in ['red', 'maroon', 'burgundy']:
                response += f"• Date nights ✓\n• Parties ✓\n• Special events ✓\n• Confidence boost days!\n\n"
            else:
                response += f"• Casual hangouts ✓\n• Weekend outings ✓\n• Fun events ✓\n• Everyday wear!\n\n"
            
            # Add similar items from dataset
            if dataset_insights.get('similar_outfits'):
                response += f"**💎 Similar Styles in Our Collection:**\n"
                for i, outfit in enumerate(dataset_insights['similar_outfits'][:3], 1):
                    outfit_name = outfit['filename'].replace('.jpg', '').replace('_', ' ').title()
                    response += f"{i}. {outfit_name}\n"
                response += "\n"
            
            # Add final thoughts
            response += f"**✨ Final Thoughts:**\n"
            response += f"Your {primary_color} {primary_clothing} is versatile and stylish! The key is pairing it with "
            response += f"complementary colors and keeping the rest of your outfit balanced. Most importantly, "
            response += f"wear it with confidence - that's your best accessory! 💕\n"
        
        return response
    
    def _handle_what_to_wear_question(self, message: str, colors: List[str], clothing: List[str], dataset_insights: Dict) -> str:
        """Handle 'what to wear' type questions"""
        response = "**Great question! Here's what I suggest: ✨**\n\n"
        
        primary_color = colors[0] if colors else None
        
        if primary_color:
            response += f"**For Your {primary_color.title()} Item:**\n\n"
            
            if primary_color in self.color_pairings:
                color_info = self.color_pairings[primary_color]
                response += f"**🎨 Colors That Work Beautifully:**\n"
                for i, match in enumerate(color_info['best_matches'][:6], 1):
                    response += f"{i}. {match.title()}\n"
                response += f"\n"
                
                if color_info['avoid']:
                    response += f"**⚠️ Colors to Avoid:** {', '.join(color_info['avoid'])}\n\n"
                
                response += f"**💡 Pro Tip:** {color_info['style_tips']}\n\n"
            
            # Specific outfit suggestions
            response += f"**👗 Complete Outfit Ideas:**\n\n"
            
            if 'top' in message or 'shirt' in message or 'blouse' in message:
                response += f"**Bottom Options:**\n"
                response += f"• White or black jeans (classic & safe)\n"
                response += f"• Denim (always works!)\n"
                response += f"• Navy or beige pants (sophisticated)\n"
                response += f"• Black skirt (feminine & chic)\n\n"
            else:
                response += f"**Top Options:**\n"
                response += f"• White t-shirt or blouse (fresh & clean)\n"
                response += f"• Black top (sleek & elegant)\n"
                response += f"• Neutral colors (beige, cream, gray)\n"
                response += f"• Denim shirt (casual & cool)\n\n"
            
            response += f"**👠 Complete the Look:**\n"
            response += f"• Shoes: White sneakers (casual) or black heels (dressy)\n"
            response += f"• Accessories: Keep simple - small earrings, delicate necklace\n"
            response += f"• Bag: Neutral color that matches your shoes\n"
        
        return response
    
    def _handle_color_matching_question(self, colors: List[str], clothing: List[str], message: str, dataset_insights: Dict) -> str:
        """Handle color matching questions"""
        response = "**Color Matching Made Easy! 🎨**\n\n"
        
        if colors:
            for color in colors[:2]:  # Handle up to 2 colors
                if color in self.color_pairings:
                    color_info = self.color_pairings[color]
                    response += f"**{color.title()} Pairs Perfectly With:**\n"
                    for match in color_info['best_matches'][:5]:
                        response += f"✓ {match.title()}\n"
                    response += f"\n💡 {color_info['style_tips']}\n\n"
        else:
            # General color matching advice
            response += "**Universal Color Pairing Rules:**\n\n"
            response += "**Safe Combinations:**\n"
            response += "• Black + White (timeless)\n"
            response += "• Navy + White (classic)\n"
            response += "• Denim + Any Color (versatile)\n"
            response += "• Neutrals + One Bright Color (balanced)\n\n"
            
            response += "**Color Wheel Basics:**\n"
            response += "• Complementary colors (opposite on wheel) create contrast\n"
            response += "• Analogous colors (next to each other) are harmonious\n"
            response += "• Monochrome (same color, different shades) is sophisticated\n"
        
        return response
    
    def _handle_occasion_question(self, occasions: List[str], colors: List[str], clothing: List[str], dataset_insights: Dict) -> str:
        """Handle occasion-based questions"""
        occasion = occasions[0] if occasions else 'general'
        response = f"**Perfect Outfit for {occasion.title()}! 👗**\n\n"
        
        # Occasion-specific advice
        occasion_guides = {
            'casual': {
                'outfit': 'Jeans + nice top + sneakers or flats',
                'colors': 'Any colors work! Have fun with it',
                'tips': 'Comfort is key. Layer with a denim jacket or cardigan.'
            },
            'formal': {
                'outfit': 'Dress or blazer + dress pants + heels',
                'colors': 'Stick to neutrals (black, navy, gray) or jewel tones',
                'tips': 'Keep it polished and professional. Minimal accessories.'
            },
            'party': {
                'outfit': 'Dress or dressy top + skirt + heels',
                'colors': 'Bold colors, metallics, or classic black',
                'tips': 'Add statement jewelry and a clutch. Go for glamour!'
            },
            'wedding': {
                'outfit': 'Elegant dress or ethnic wear + heels',
                'colors': 'Avoid white! Pastels, jewel tones, or traditional colors',
                'tips': 'Dress code matters - check if it\'s traditional or western.'
            },
            'work': {
                'outfit': 'Blouse + pants/skirt + closed-toe shoes',
                'colors': 'Professional colors - navy, black, gray, white, pastels',
                'tips': 'Keep it conservative. Blazer adds polish.'
            },
            'date': {
                'outfit': 'Something that makes you feel confident!',
                'colors': 'Red (bold), pink (feminine), or your best color',
                'tips': 'Wear what makes YOU feel amazing. Confidence is sexy!'
            }
        }
        
        if occasion in occasion_guides:
            guide = occasion_guides[occasion]
            response += f"**👗 Outfit Formula:**\n{guide['outfit']}\n\n"
            response += f"**🎨 Color Choices:**\n{guide['colors']}\n\n"
            response += f"**💡 Pro Tips:**\n{guide['tips']}\n"
        
        return response
    
    def _handle_uncertainty_question(self, message: str, colors: List[str], clothing: List[str], dataset_insights: Dict) -> str:
        """Handle questions where user is uncertain"""
        response = "**Don't worry, I've got you! Let me break it down: 💕**\n\n"
        
        if colors and clothing:
            color = colors[0]
            item = clothing[0]
            response += f"**For Your {color.title()} {item.title()}:**\n\n"
            response += "**Easy Pairing Formula:**\n"
            response += f"1. **Safe Choice:** Pair with white, black, or denim\n"
            response += f"2. **Stylish Choice:** Add neutral bottoms/tops\n"
            response += f"3. **Bold Choice:** Monochrome or complementary colors\n\n"
        
        response += "**When In Doubt, Remember:**\n"
        response += "• Neutrals (black, white, beige, navy) go with EVERYTHING\n"
        response += "• Denim is your best friend - works with all colors\n"
        response += "• Keep it simple - 2-3 colors max in one outfit\n"
        response += "• Confidence is your best accessory!\n\n"
        
        response += "**Quick Decision Guide:**\n"
        response += "1. Pick your statement piece (the colorful item)\n"
        response += "2. Pair with neutrals\n"
        response += "3. Add simple accessories\n"
        response += "4. You're done! ✨\n"
        
        return response
    
    def _generate_default_intelligent_response(self, message: str, nlp_context: Dict, dataset_insights: Dict) -> str:
        """Generate intelligent default response with specific advice"""
        entities = nlp_context.get('entities', {})
        colors = entities.get('colors', [])
        clothing = entities.get('clothing_types', [])
        
        # Try to give specific advice based on what was mentioned
        if colors or clothing:
            response = "**Perfect! Let me help you with that! 💕**\n\n"
            
            # Handle colors mentioned
            if colors:
                primary_color = colors[0]
                if primary_color in self.color_pairings:
                    color_info = self.color_pairings[primary_color]
                    response += f"**Styling {primary_color.title()}:**\n\n"
                    response += f"**🎨 Best Color Matches:**\n"
                    for match in color_info['best_matches'][:5]:
                        response += f"• {match.title()}\n"
                    response += f"\n💡 {color_info['style_tips']}\n\n"
            
            # Handle clothing mentioned
            if clothing:
                primary_item = clothing[0]
                if primary_item in self.clothing_advice:
                    item_info = self.clothing_advice[primary_item]
                    response += f"**Styling Your {primary_item.title()}:**\n\n"
                    response += f"• {item_info['style']}\n"
                    response += f"• Perfect for: {', '.join(item_info['occasions'])}\n\n"
                    
                    # Add specific outfit ideas
                    if primary_item in ['top', 'shirt', 'blouse']:
                        response += "**Complete Outfit Ideas:**\n"
                        response += "1. Pair with black or white jeans\n"
                        response += "2. Add a denim jacket for casual\n"
                        response += "3. Tuck into a skirt for dressy\n"
                        response += "4. Layer under a blazer for work\n\n"
                    elif primary_item in ['jeans', 'pants', 'skirt']:
                        response += "**Complete Outfit Ideas:**\n"
                        response += "1. White or black top (classic)\n"
                        response += "2. Fitted sweater (cozy)\n"
                        response += "3. Blouse + blazer (professional)\n"
                        response += "4. Graphic tee (casual)\n\n"
            
            # Add similar items from dataset if available
            if dataset_insights.get('similar_outfits'):
                response += "**💎 Inspiration from Our Collection:**\n"
                for i, outfit in enumerate(dataset_insights['similar_outfits'][:3], 1):
                    outfit_name = outfit['filename'].replace('.jpg', '').replace('_', ' ').title()
                    response += f"{i}. {outfit_name}\n"
                response += "\n"
        
        else:
            # General fashion advice when no specific items mentioned
            response = "**Fashion Styling Guide! ✨**\n\n"
            
            response += "**🎨 Color Coordination Basics:**\n"
            response += "• **Neutrals** (black, white, beige, navy) go with everything\n"
            response += "• **Denim** is your best friend - pairs with all colors\n"
            response += "• **Monochrome** (same color, different shades) looks sophisticated\n"
            response += "• **Pop of color** - one bright piece with neutrals\n\n"
            
            response += "**👗 Outfit Building Formula:**\n"
            response += "1. Start with a base (neutral bottom or dress)\n"
            response += "2. Add a complementary top\n"
            response += "3. Layer if needed (jacket, cardigan)\n"
            response += "4. Accessorize (shoes, bag, jewelry)\n"
            response += "5. Check proportions (fitted + loose balance)\n\n"
            
            response += "**💡 Quick Style Tips:**\n"
            response += "• **Casual:** Jeans + nice top + sneakers\n"
            response += "• **Work:** Blazer + blouse + trousers\n"
            response += "• **Date:** Dress or fitted top + skirt\n"
            response += "• **Party:** Statement piece + heels\n\n"
            
            response += "**✨ Remember:**\n"
            response += "• Fit is everything - wear your size!\n"
            response += "• Confidence is your best accessory\n"
            response += "• When in doubt, keep it simple\n"
            response += "• Have fun with fashion! 💕\n"
        
        return response
    
    def _add_dataset_footer(self, dataset_insights: Dict) -> str:
        """Add dataset information footer"""
        footer = "\n\n---\n"
        footer += "**📊 Analysis powered by:**\n"
        stats = dataset_insights.get('dataset_stats', {})
        footer += f"• {stats.get('total_fashion_images', 0)} fashion images\n"
        footer += f"• {stats.get('body_profiles', 0)} body profile insights\n"
        footer += "• Advanced NLP & Computer Vision\n"
        return footer

# Create global instance
smart_generator = SmartResponseGenerator()
