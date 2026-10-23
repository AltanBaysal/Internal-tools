# Krea prompt writing

## The image model
- The photo of each frame is made by the Krea image model, which reads plain English sentences.
- The image model was trained on sentences, not on tags. So was the LoRA it draws with.
- Long, detailed prompts give the best photos. A short prompt works too, with less control.
- The photo is made at 1280 x 720 for a landscape video, 16:9, or at 832 x 1248 for a portrait video, 2:3.

## The style
- The scenario has one style: one or two sentences naming the medium and the look of every photo, as in: A photorealistic photo taken on a phone, in soft daylight.
- The style is the user's, asked when the scenario starts.
- The code puts the style in front of the prompt of every frame. So the prompt of a frame never says the style again: it starts with what is in the photo.

## The prompt of a frame
- The photo is the first moment of the scene: the video starts from the photo.
- Write the prompt in English, as one paragraph of plain sentences. No lists, no headings.
- Say who is in the photo, how each person looks and what each person wears, what is happening, where it happens, the light, and how close the camera is and from where it looks.
- The photo has the orientation of the video, landscape or portrait. Choose how close the camera is and where each person is in the photo to fit the orientation.
- Keep each person's look and action together, in the same sentences, so the image model knows whose is whose.
- When the photo holds two or more people, say where each person is in the photo, as in on the left, on the right or behind her, and what each person does.
- Words written in the photo itself, as on a sign or a shirt, go inside quotes.
- If the scene is NSFW, say what is happening in plain sentences, and name each visible body part directly, as in penis or vagina.

## What is left out
- Never write tags or a comma-separated list of keywords. The image model reads sentences.
- Never write quality words such as masterpiece, best quality or 4k. They come from image models trained on tags, and this one reads sentences.
- Never write BREAK. The image model reads BREAK as one more word.
- Never write weights such as (smile:1.2). The image model does not read weights.
- Never write a LoRA trigger word. The LoRA the image model draws with has none.
- Never write a negative list. The photo is made at cfg 1, where the image model reads no negative prompt. Write what the photo shows instead.

## The scene
- Write each scene in English.
- Write each scene in sentences, never as tags.
- Write the words a character says inside quotes, in natural, well-written English. Translate the words when the user gives the words in another language.
- Write each scene short enough for the video length: how many seconds the video of each frame is.
- Each scene is used later to write the prompt for the video model.
