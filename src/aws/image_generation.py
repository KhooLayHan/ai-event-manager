import json
import base64
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

def generate_optimized_venue_image(ai_recommendations, venue_type="concert_venue"):
    """Generate optimized venue layout image using Amazon Titan Image Generator"""
    
    try:
        bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name="us-east-1",
            config=Config(retries={"max_attempts": 3})
        )
        
        # Create detailed prompt for venue optimization
        prompt = f"""
        Create a professional top-down architectural diagram of an optimized {venue_type.replace('_', ' ')} layout:
        
        OPTIMIZED FEATURES:
        - {ai_recommendations['optimized_parameters']['recommended_open_gates']} entry gates (bright green rectangles)
        - {ai_recommendations['optimized_parameters']['recommended_staff']} staff positions (blue circles with 'S')
        - 2 emergency exits (red rectangles with 'EXIT')
        - Food/facility areas (yellow squares)
        - Clear crowd flow paths (curved arrows showing movement)
        - Open walkable areas (light gray)
        - Safety barriers where needed (black lines)
        
        STYLE: Clean architectural blueprint, bird's eye view, professional venue design
        COLORS: Green gates, red exits, blue staff, yellow facilities, gray walkways
        LABELS: Clear text labels for each element
        """
        
        request_body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt,
                "negativeText": "blurry, low quality, messy, unclear, amateur"
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "height": 768,
                "width": 768,
                "cfgScale": 8.0,
                "seed": 42
            }
        }
        
        logger.info("Generating optimized venue image with Titan Image Generator...")
        response = bedrock_runtime.invoke_model(
            modelId="amazon.titan-image-generator-v1",
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response["body"].read())
        
        # Extract base64 image
        if "images" in response_body and len(response_body["images"]) > 0:
            base64_image = response_body["images"][0]
            
            # Save image to temp folder
            from pathlib import Path
            output_path = Path(__file__).parent.parent.parent / "temp" / "optimized_venue.png"
            output_path.parent.mkdir(exist_ok=True)
            
            # Decode and save
            image_data = base64.b64decode(base64_image)
            with open(output_path, "wb") as f:
                f.write(image_data)
            
            logger.info(f"Optimized venue image saved to {output_path}")
            return str(output_path), base64_image
        
        else:
            logger.error("No images returned from Titan Image Generator")
            return None, None
            
    except ClientError as e:
        logger.error(f"AWS ClientError generating image: {e}")
        return None, None
    except Exception as e:
        logger.error(f"Error generating optimized venue image: {e}")
        return None, None

def create_before_after_comparison(before_image_path, optimized_image_base64, ai_recommendations):
    """Create a before/after comparison image showing the optimization"""
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Load before image
        before_img = Image.open(before_image_path)
        
        # Decode optimized image
        optimized_img_data = base64.b64decode(optimized_image_base64)
        optimized_img = Image.open(io.BytesIO(optimized_img_data))
        
        # Resize to same dimensions
        target_size = (400, 400)
        before_img = before_img.resize(target_size)
        optimized_img = optimized_img.resize(target_size)
        
        # Create comparison image
        comparison_width = target_size[0] * 2 + 50  # Gap between images
        comparison_height = target_size[1] + 100    # Space for text
        
        comparison = Image.new('RGB', (comparison_width, comparison_height), 'white')
        
        # Paste images
        comparison.paste(before_img, (0, 50))
        comparison.paste(optimized_img, (target_size[0] + 50, 50))
        
        # Add labels
        draw = ImageDraw.Draw(comparison)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        draw.text((100, 10), "BEFORE AI", fill='red', font=font)
        draw.text((target_size[0] + 150, 10), "AFTER AI", fill='green', font=font)
        
        # Add improvement metrics
        improvements = [
            f"Gates: {ai_recommendations['optimized_parameters']['recommended_open_gates']}",
            f"Staff: {ai_recommendations['optimized_parameters']['recommended_staff']}",
            f"Staggered Entry: {'Yes' if ai_recommendations['optimized_parameters']['staggered_entry'] else 'No'}"
        ]
        
        y_pos = target_size[1] + 60
        for improvement in improvements:
            draw.text((10, y_pos), improvement, fill='black', font=font)
            y_pos += 25
        
        # Save comparison
        from pathlib import Path
        output_path = Path(__file__).parent.parent.parent / "temp" / "before_after_comparison.png"
        comparison.save(output_path)
        
        logger.info(f"Before/after comparison saved to {output_path}")
        return str(output_path)
        
    except Exception as e:
        logger.error(f"Error creating before/after comparison: {e}")
        return None