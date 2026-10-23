# SDXL prompt writing

## The image model
- The photo of each frame is made by an SDXL-family image model trained on Danbooru's own tags, at 1536 x 864 for a landscape video, 16:9, or at 1024 x 1536 for a portrait video, 2:3.
- The image model reads the tags of every entry and of every frame's action.
- The image model is weak and draws every tag in the prompt. A complex prompt breaks the image.

## Writing a tag
- Write tags, never sentences. An article is not a tag either.
- Use a tag that the Danbooru vocabulary already has, rather than a description of the same thing. The model has seen a real tag many times, and has never seen a paraphrase of it.
- Write the tags in English, with spaces where the site writes underscores.
- Put one thing in each tag, split the way the vocabulary splits it. Do not join two tags into one longer phrase.
- When the vocabulary has no tag for it, write a few plain words in the same short form.

## What is left out
- Never write quality tags. The code already puts them at the front of every prompt, so yours would be printed twice.
- Never write the word or inside a tag. The model draws one picture and cannot toss a coin between two choices, so pick one and write only that.
- Never write solo in a character's entry. The same character stands alone in one frame and next to somebody in the next, so an entry claiming solo is wrong in half of them.
- Never add a mirror unless the user asks for one. A mirror breaks the image.

## The prompt of a frame
- The code builds every frame's prompt in a fixed order, so a character reads the same in all of them.
- Whoever is written first among a frame's characters leads the frame's prompt.
- The prompt of a frame describes one photo: the first moment of the scene.
- Some tags are not visible from some camera angles. So a character, an outfit or a place can have more than one entry, for different camera angles.
- The most common mistake: a tag hidden by the camera angle goes onto another character. For example, the hair of a hidden head ends up on another character.
- Rule 1: If one of the character's entries fits the camera angle, use the entry. An entry fits when every tag of the entry is meant to be in the photo. If no entry fits, add a new entry with only the tags meant to be in the photo.
- Rule 2: If one of the outfit's entries fits the camera angle, use the entry. An entry fits when every tag of the entry is meant to be in the photo. If no entry fits, add a new entry with only the tags meant to be in the photo.
- Rule 3: If one of the place's entries fits the camera angle, use the entry. An entry fits when every tag of the entry is meant to be in the photo. If no entry fits, add a new entry with only the tags meant to be in the photo.
- Rule 4: The image model draws one photo. The whole prompt of the frame must describe only one photo. If the prompt describes more than one photo, remove the extra part.
- Rule 5: The whole prompt of the frame must be simple enough for the weak image model. If a part of the prompt is too hard, make the part simpler, and keep the same moment.
- Rule 6: If the scene is NSFW, name each visible body part directly, as in penis or vagina. Never use a euphemism.
- Rule 7: The photo has the orientation of the video, landscape or portrait. Choose the camera angle and where each character is in the photo to fit the orientation.

## The negative list
- The negative list is for the image model, not the video model. The negative list tells the image model what not to draw in the photo.
- The scenario has one negative list, for every frame. A tag in the negative list works on the whole photo, not on one character.
- The biggest problem is the features of the characters mixing, as in the hair of one character on another character. Focus the negative list on keeping the features of each character apart.
- Never write a feature of a character into the negative list. For example, dark skin in the negative list made a dark-skinned man come out white.
- To keep a feature of a character, write the opposite tags instead. For example, pale male and white man for a dark-skinned man.

## The scene
- Write each scene in English.
- Write each scene in sentences, never as tags.
- Write the words a character says inside quotes, in natural, well-written English. Translate the words when the user gives the words in another language.
- Write each scene short enough for the video length: how many seconds the video of each frame is.
- Each scene is used later to write the prompt for the video model.
