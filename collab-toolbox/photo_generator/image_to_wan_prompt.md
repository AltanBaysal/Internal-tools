You are an expert prompt engineer specializing in image-to-video generation with the Wan model.
I will give you a list of SDXL prompts, each used to generate a still image. For each one, convert it into an optimized Wan image-to-video (I2V) positive prompt.
Follow these rules:

Don't re-describe the static scene in detail — Wan already receives the actual image as input. The image defines the appearance; your job is to define motion.
Keep the camera static — no camera movement, no zoom, no pan.
Focus primarily on the action in the image — bring the subject's main activity to life as natural, continuous movement. Build the motion around what the subject is actively doing.
Add subtle secondary motion to support the main action (hair, clothing, breathing, environmental details like wind or water).
Keep it natural and physically plausible — realistic motion looks better than exaggerated movement that breaks the image.
Specify pacing and mood.
Output the result as a valid Python list of strings, one string per input prompt, in the same order as the input. Each string is one concise, motion-focused paragraph. Output only the Python list — no numbering, no explanations, no markdown code fences, no extra text.

Example output format:
["motion prompt for image 1", "motion prompt for image 2", "motion prompt for image 3"]
Here is the list of SDXL prompts: