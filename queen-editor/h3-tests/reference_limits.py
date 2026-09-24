PROMPTS = [
# 1 -- the woman in Picture 1 stands still, the camera orbits her a full 360 degrees
"""
subject_definitions:
<Subject 1> is the anime-styled young woman in <Picture 1>, with long straight hair that is black at the roots and fades to blonde toward the ends, side-swept bangs covering her right eye, a black glossy corset with pink lace-up ribbons and pink lace trim, and a black-and-pink choker.
<Subject 2> is the 3D anime CG render style of <Picture 1>, applied to the whole frame -- the woman, the environment, every prop and the light: cel-shaded toon shading with soft stylised shadows, smooth flawless skin with no pores or skin texture, large expressive anime eyes, glossy clean highlights on hair and clothing, and clean stylised anime backgrounds.

summary:
[reference generation] <Subject 1> stands still in a plain studio while the camera orbits a full circle around her, showing her from every side, including her back, the back of her hair, and the back of her outfit, which <Picture 1> does not show. The whole video stays in <Subject 2>.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, two-tone hair, bangs, corset, and choker from <Picture 1> are retained from every angle.
<Subject 2> (appears in [Shot 1]): fully_preserved - the 3D anime CG render style of <Picture 1> covers every frame, the environment and props as much as the woman; nothing turns live-action or photorealistic.

detailed_description:
The whole video is a stylised 3D anime CG animation in <Subject 2>, not live-action footage and not photorealistic, with soft, even studio lighting.
[Shot 1] A medium-full shot shows <Subject 1>, the anime-styled young woman with long hair that is black at the roots and blonde toward the ends, side-swept bangs over her right eye, a black glossy corset with pink lace-up ribbons and pink lace trim, and a black-and-pink choker, standing still on a plain light-grey studio floor in front of a seamless light-grey background, drawn in <Subject 2> like her. She is the only person in the frame. She keeps her pose, her arms relaxed at her sides, and only blinks and breathes. The camera orbits around her with large amplitude at a steady, fairly fast speed, making one full 360-degree circle at the same distance and height: it passes her left side, shows her full back, the back of her long two-tone hair and the back of her corset and its lacing, passes her right side, and returns to the front view by the last frame. Her face, hair, and outfit stay the same throughout the orbit, and every angle stays in <Subject 2>.

overall_soundscape:
Quiet studio room tone with no other sound.

non_diegetic_music:
N/A
""",
# 1 -- the woman in Picture 2 stands still, the camera orbits her a full 360 degrees
"""
subject_definitions:
<Subject 1> is the anime-styled young woman in <Picture 2>, with long straight black hair, dark gothic eye makeup and dark lipstick, gold hoop earrings, a black choker, a black off-shoulder cropped top, and a colourful floral tattoo sleeve on her left arm.
<Subject 2> is the 3D anime CG render style of <Picture 2>, applied to the whole frame -- the woman, the environment, every prop and the light: cel-shaded toon shading with soft stylised shadows, smooth flawless skin with no pores or skin texture, large expressive anime eyes, glossy clean highlights on hair and clothing, and clean stylised anime backgrounds.

summary:
[reference generation] <Subject 1> stands still in a plain studio while the camera orbits a full circle around her, showing her from every side, including her back, the back of her hair, and the back of her outfit, which <Picture 2> does not show. The whole video stays in <Subject 2>.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, black hair, gothic makeup, earrings, choker, cropped top, and arm tattoo from <Picture 2> are retained from every angle.
<Subject 2> (appears in [Shot 1]): fully_preserved - the 3D anime CG render style of <Picture 2> covers every frame, the environment and props as much as the woman; nothing turns live-action or photorealistic.

detailed_description:
The whole video is a stylised 3D anime CG animation in <Subject 2>, not live-action footage and not photorealistic, with soft, even studio lighting.
[Shot 1] A medium-full shot shows <Subject 1>, the anime-styled young woman with long straight black hair, dark gothic makeup, gold hoop earrings, a black choker, a black off-shoulder cropped top, and a colourful floral tattoo sleeve on her left arm, standing still on a plain light-grey studio floor in front of a seamless light-grey background, drawn in <Subject 2> like her. She is the only person in the frame. She keeps her pose, one hand resting on her hip, and only blinks and breathes. The camera orbits around her with large amplitude at a steady, fairly fast speed, making one full 360-degree circle at the same distance and height: it passes her left side and the tattooed arm, shows her full back, the back of her long black hair and the back of her cropped top, passes her right side, and returns to the front view by the last frame. Her face, hair, tattoo, and outfit stay the same throughout the orbit, and every angle stays in <Subject 2>.

overall_soundscape:
Quiet studio room tone with no other sound.

non_diegetic_music:
N/A
""",
# 2 -- the woman in Picture 1 looks into the camera and says one short Turkish sentence
"""
subject_definitions:
<Subject 1> is the anime-styled young woman in <Picture 1>, with long straight hair that is black at the roots and fades to blonde toward the ends, side-swept bangs covering her right eye, a black glossy corset with pink lace-up ribbons and pink lace trim, and a black-and-pink choker.
<Subject 2> is the 3D anime CG render style of <Picture 1>, applied to the whole frame -- the woman, the environment, every prop and the light: cel-shaded toon shading with soft stylised shadows, smooth flawless skin with no pores or skin texture, large expressive anime eyes, glossy clean highlights on hair and clothing, and clean stylised anime backgrounds.

summary:
[reference generation] <Subject 1> looks straight into the camera in her dark ornate room and says one short sentence in Turkish, testing lip sync and voice. The whole video stays in <Subject 2>.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, two-tone hair, bangs, corset, and choker from <Picture 1> are retained.
<Subject 2> (appears in [Shot 1]): fully_preserved - the 3D anime CG render style of <Picture 1> covers every frame, the environment and props as much as the woman; nothing turns live-action or photorealistic.

detailed_description:
The whole video is a stylised 3D anime CG animation in <Subject 2>, not live-action footage and not photorealistic, with warm, dim interior lighting.
[Shot 1] A medium close-up shows <Subject 1> (S1), the anime-styled young woman with long hair that is black at the roots and blonde toward the ends, side-swept bangs over her right eye, a black glossy corset with pink lace trim, and a black-and-pink choker, standing in a dark room with ornate wooden columns and dark damask wallpaper behind her, the room drawn in <Subject 2> like her. She is the only person in the frame. She looks straight into the lens, smiles softly, and says in a warm, gentle young female voice at a calm pace, <d>[Turkish] Merhaba, bugün seninle bir şey paylaşacağım.</d> Her anime mouth moves in time with every syllable, and she tilts her head slightly at the end of the line and keeps smiling. The camera stays still.

overall_soundscape:
Quiet indoor room tone behind her voice.

non_diegetic_music:
N/A
""",
# 3 -- the woman in Picture 2 in a completely different place: a rainy city street at night
"""
subject_definitions:
<Subject 1> is the anime-styled young woman in <Picture 2>, with long straight black hair, dark gothic eye makeup and dark lipstick, gold hoop earrings, a black choker, a black off-shoulder cropped top, and a colourful floral tattoo sleeve on her left arm.
<Subject 2> is the 3D anime CG render style of <Picture 2>, applied to the whole frame -- the woman, the environment, every prop and the light: cel-shaded toon shading with soft stylised shadows, smooth flawless skin with no pores or skin texture, large expressive anime eyes, glossy clean highlights on hair and clothing, and clean stylised anime backgrounds.

summary:
[reference generation] <Subject 1> stands on a rainy city street at night, far from the white hallway of <Picture 2>, and looks around, testing whether her identity holds in a completely new environment and light. The new street is drawn in <Subject 2> as well.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, black hair, gothic makeup, earrings, choker, cropped top, and arm tattoo from <Picture 2> are retained; the background of <Picture 2> is not used.
<Subject 2> (appears in [Shot 1]): fully_preserved - the 3D anime CG render style of <Picture 2> covers every frame, the street, the rain and the neon as much as the woman; nothing turns live-action or photorealistic.

detailed_description:
The whole video is a stylised 3D anime CG animation in <Subject 2>, not live-action footage and not photorealistic, with cold blue night light and pink and blue neon glow.
[Shot 1] A medium shot shows <Subject 1>, the anime-styled young woman with long straight black hair, dark gothic makeup, gold hoop earrings, a black choker, a black off-shoulder cropped top, and a floral tattoo sleeve on her left arm, standing on a narrow anime city street at night in light rain. She is the only person in the frame. The street, the shop signs and the rain are drawn in <Subject 2> like her: the wet asphalt shows clean stylised reflections of the neon signs, and the raindrops fall as simple bright streaks. She looks to her left, then turns her head back toward the camera and pushes a strand of black hair behind her ear. The camera pushes in with small amplitude at slow speed.

overall_soundscape:
Steady light rain patters on the pavement and nearby awnings, with the distant hum of city traffic.

non_diegetic_music:
N/A
""",
# 4 -- the woman in Picture 1 stands still, the camera pushes in to her face
"""
subject_definitions:
<Subject 1> is the anime-styled young woman in <Picture 1>, with long straight hair that is black at the roots and fades to blonde toward the ends, side-swept bangs covering her right eye, a black glossy corset with pink lace-up ribbons and pink lace trim, and a black-and-pink choker.
<Subject 2> is the 3D anime CG render style of <Picture 1>, applied to the whole frame -- the woman, the environment, every prop and the light: cel-shaded toon shading with soft stylised shadows, smooth flawless skin with no pores or skin texture, large expressive anime eyes, glossy clean highlights on hair and clothing, and clean stylised anime backgrounds.

summary:
[reference generation] <Subject 1> stands still while the camera pushes in from a medium shot to a close-up of her face, testing facial detail at close range. The close-up stays in <Subject 2>.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, two-tone hair, bangs, corset, and choker from <Picture 1> are retained, and her face stays sharp in close-up.
<Subject 2> (appears in [Shot 1]): fully_preserved - the 3D anime CG render style of <Picture 1> covers every frame, the close-up of her face included; nothing turns live-action or photorealistic.

detailed_description:
The whole video is a stylised 3D anime CG animation in <Subject 2>, not live-action footage and not photorealistic, with warm, dim interior lighting.
[Shot 1] A medium shot shows <Subject 1>, the anime-styled young woman with long hair that is black at the roots and blonde toward the ends, side-swept bangs over her right eye, a black glossy corset with pink lace trim, and a black-and-pink choker, standing in her dark room with ornate wooden columns and dark damask wallpaper, the room drawn in <Subject 2> like her. She is the only person in the frame. She stays still, looking into the lens with a soft smile, and blinks once. The camera pushes in with large amplitude at a steady, slow speed, from her waist up to a tight close-up of her face that fills the frame by the last frame. Up close her face keeps the anime look of <Subject 2>: smooth flawless skin, a large glossy anime eye, the bangs across the other eye, soft stylised lips, and the choker at her neck, all sharp and unchanged.

overall_soundscape:
Quiet indoor room tone.

non_diegetic_music:
N/A
""",
# 5 -- the woman in Picture 2 stands still, the camera pulls back and rises to show her full body
"""
subject_definitions:
<Subject 1> is the anime-styled young woman in <Picture 2>, with long straight black hair, dark gothic eye makeup and dark lipstick, gold hoop earrings, a black choker, a black off-shoulder cropped top, and a colourful floral tattoo sleeve on her left arm.
<Subject 2> is the 3D anime CG render style of <Picture 2>, applied to the whole frame -- the woman, the environment, every prop and the light: cel-shaded toon shading with soft stylised shadows, smooth flawless skin with no pores or skin texture, large expressive anime eyes, glossy clean highlights on hair and clothing, and clean stylised anime backgrounds.

summary:
[reference generation] <Subject 1> stands on a sunny rooftop while the camera pulls back and rises, going from her face to her full body and the city around her, testing whole-body consistency. The rooftop and the city are drawn in <Subject 2> as well.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, black hair, gothic makeup, earrings, choker, cropped top, and arm tattoo from <Picture 2> are retained, and her full body stays consistent with them.
<Subject 2> (appears in [Shot 1]): fully_preserved - the 3D anime CG render style of <Picture 2> covers every frame, the rooftop and the city as much as the woman; nothing turns live-action or photorealistic.

detailed_description:
The whole video is a stylised 3D anime CG animation in <Subject 2>, not live-action footage and not photorealistic, with bright afternoon sunlight.
[Shot 1] The shot opens on a close-up of <Subject 1>, the anime-styled young woman with long straight black hair, dark gothic makeup, gold hoop earrings, and a black choker, standing on a flat rooftop. She is the only person in the frame. She looks up into the lens and smiles. The camera pulls back with large amplitude and cranes up at the same time at a steady speed, revealing her black off-shoulder cropped top, the floral tattoo sleeve on her left arm, her legs and feet, and finally her whole body standing still in the middle of the rooftop. By the last frame the anime city around her fills the view: simple stylised buildings with clean shapes and flat bright windows under a clear blue anime sky, all drawn in <Subject 2> like her. A light breeze moves her hair.

overall_soundscape:
Wind moves across the rooftop, with the distant sound of city traffic below.

non_diegetic_music:
N/A
""",
# 6 -- a handheld-style camera follows the woman in Picture 1 as she walks
"""
subject_definitions:
<Subject 1> is the anime-styled young woman in <Picture 1>, with long straight hair that is black at the roots and fades to blonde toward the ends, side-swept bangs covering her right eye, a black glossy corset with pink lace-up ribbons and pink lace trim, and a black-and-pink choker.
<Subject 2> is the 3D anime CG render style of <Picture 1>, applied to the whole frame -- the woman, the environment, every prop and the light: cel-shaded toon shading with soft stylised shadows, smooth flawless skin with no pores or skin texture, large expressive anime eyes, glossy clean highlights on hair and clothing, and clean stylised anime backgrounds.

summary:
[reference generation] A handheld-style camera follows <Subject 1> from behind and to the side as she walks through a busy street market, testing whether the camera style is followed. The market is drawn in <Subject 2> as well.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, two-tone hair, bangs, corset, and choker from <Picture 1> are retained while she walks.
<Subject 2> (appears in [Shot 1]): fully_preserved - the 3D anime CG render style of <Picture 1> covers every frame, the market, the stalls and the people as much as the woman; nothing turns live-action or photorealistic.

detailed_description:
The whole video is a stylised 3D anime CG animation in <Subject 2>, not live-action footage and not photorealistic, with warm late-afternoon light.
[Shot 1] A medium shot follows <Subject 1>, the anime-styled young woman with long hair that is black at the roots and blonde toward the ends, side-swept bangs over her right eye, a black glossy corset with pink lace trim, and a black-and-pink choker, as she walks at a relaxed pace through a narrow anime street market with colourful fruit stalls and hanging fabric awnings on both sides. The stalls, the fruit, the awnings and the few stall keepers far behind her are all drawn in <Subject 2> like her, and she is the only person in focus. The camera tracks her from slightly behind her right shoulder with a light handheld-style sway and bob. Halfway through, she glances back over her shoulder toward the camera with a playful smile, showing her face, then looks ahead again and keeps walking.

overall_soundscape:
The murmur of a busy market, footsteps on stone, and the rustle of fabric awnings in the breeze.

non_diegetic_music:
N/A
""",
# 7 -- the woman in Picture 1 opens a door and walks through
"""
subject_definitions:
<Subject 1> is the anime-styled young woman in <Picture 1>, with long straight hair that is black at the roots and fades to blonde toward the ends, side-swept bangs covering her right eye, a black glossy corset with pink lace-up ribbons and pink lace trim, and a black-and-pink choker.
<Subject 2> is the 3D anime CG render style of <Picture 1>, applied to the whole frame -- the woman, the environment, every prop and the light: cel-shaded toon shading with soft stylised shadows, smooth flawless skin with no pores or skin texture, large expressive anime eyes, glossy clean highlights on hair and clothing, and clean stylised anime backgrounds.

summary:
[reference generation] <Subject 1> walks up to a closed wooden door, turns the handle, pulls it open, and steps through, testing hand contact with an object. The hallway and the door are drawn in <Subject 2> as well.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, two-tone hair, bangs, corset, and choker from <Picture 1> are retained.
<Subject 2> (appears in [Shot 1]): fully_preserved - the 3D anime CG render style of <Picture 1> covers every frame, the hallway, the door and the room beyond as much as the woman; nothing turns live-action or photorealistic.

detailed_description:
The whole video is a stylised 3D anime CG animation in <Subject 2>, not live-action footage and not photorealistic, with warm, dim interior lighting.
[Shot 1] A medium-wide shot shows a dark anime hallway with damask wallpaper and a tall closed wooden door with a brass handle, drawn in <Subject 2> with clean shapes and glossy highlights. <Subject 1>, the anime-styled young woman with long hair that is black at the roots and blonde toward the ends, side-swept bangs over her right eye, a black glossy corset with pink lace trim, and a black-and-pink choker, walks up to the door from the left. She is the only person in the frame. She grips the brass handle with her right hand, turns it down, and pulls the door open toward her. Warm light spills out from the room beyond. She steps through the doorway and her back disappears into the lit room. Her fingers stay wrapped around the handle while she turns it, and the door swings on its hinges. The camera stays still.

overall_soundscape:
Footsteps on a wooden floor, the click of the door handle, and the creak of the hinges as the door opens.

non_diegetic_music:
N/A
""",
# 7 -- the woman in Picture 2 opens a door and walks through
"""
subject_definitions:
<Subject 1> is the anime-styled young woman in <Picture 2>, with long straight black hair, dark gothic eye makeup and dark lipstick, gold hoop earrings, a black choker, a black off-shoulder cropped top, and a colourful floral tattoo sleeve on her left arm.
<Subject 2> is the 3D anime CG render style of <Picture 2>, applied to the whole frame -- the woman, the environment, every prop and the light: cel-shaded toon shading with soft stylised shadows, smooth flawless skin with no pores or skin texture, large expressive anime eyes, glossy clean highlights on hair and clothing, and clean stylised anime backgrounds.

summary:
[reference generation] <Subject 1> walks up to a closed white door, turns the handle, pushes it open, and steps through into a garden, testing hand contact with an object. The hallway, the door and the garden are drawn in <Subject 2> as well.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, black hair, gothic makeup, earrings, choker, cropped top, and arm tattoo from <Picture 2> are retained.
<Subject 2> (appears in [Shot 1]): fully_preserved - the 3D anime CG render style of <Picture 2> covers every frame, the hallway, the door and the garden as much as the woman; nothing turns live-action or photorealistic.

detailed_description:
The whole video is a stylised 3D anime CG animation in <Subject 2>, not live-action footage and not photorealistic, with bright, soft daylight.
[Shot 1] A medium-wide shot shows a bright white anime hallway with a closed white panel door and a silver handle, drawn in <Subject 2> with clean shapes and smooth surfaces. <Subject 1>, the anime-styled young woman with long straight black hair, dark gothic makeup, gold hoop earrings, a black choker, a black off-shoulder cropped top, and a floral tattoo sleeve on her left arm, walks up to the door from the right. She is the only person in the frame. She grips the silver handle with her left hand, the tattooed arm, turns it down, and pushes the door open away from her. Daylight from an anime garden beyond the door falls on her, its grass and flowers drawn in the same style. She steps through the doorway into the garden, her long black hair swinging behind her. Her fingers stay wrapped around the handle while she turns it, and the door swings on its hinges. The camera stays still.

overall_soundscape:
Footsteps on the floor, the click of the door handle, and birdsong rising as the door opens onto the garden.

non_diegetic_music:
N/A
""",
# 8 -- the woman in Picture 2 drives a car, seen from inside
"""
subject_definitions:
<Subject 1> is the anime-styled young woman in <Picture 2>, with long straight black hair, dark gothic eye makeup and dark lipstick, gold hoop earrings, a black choker, a black off-shoulder cropped top, and a colourful floral tattoo sleeve on her left arm.
<Subject 2> is the 3D anime CG render style of <Picture 2>, applied to the whole frame -- the woman, the environment, every prop and the light: cel-shaded toon shading with soft stylised shadows, smooth flawless skin with no pores or skin texture, large expressive anime eyes, glossy clean highlights on hair and clothing, and clean stylised anime backgrounds.

summary:
[reference generation] <Subject 1> drives a car along a coastal road, seen from the passenger seat, testing a seated pose, hands on the wheel, and motion outside the windows. The car and the road are drawn in <Subject 2> as well.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, black hair, gothic makeup, earrings, choker, cropped top, and arm tattoo from <Picture 2> are retained while she sits and drives.
<Subject 2> (appears in [Shot 1]): fully_preserved - the 3D anime CG render style of <Picture 2> covers every frame, the car interior and the coast outside as much as the woman; nothing turns live-action or photorealistic.

detailed_description:
The whole video is a stylised 3D anime CG animation in <Subject 2>, not live-action footage and not photorealistic, with bright afternoon sunlight coming through the car windows.
[Shot 1] A medium shot from the passenger seat shows <Subject 1>, the anime-styled young woman with long straight black hair, dark gothic makeup, gold hoop earrings, a black choker, a black off-shoulder cropped top, and a floral tattoo sleeve on her left arm, sitting in the driver's seat of an anime car with a clean, simply shaped dashboard. She is the only person in the car. Both her hands hold the steering wheel, and she turns it slightly to follow a gentle curve. Through the side window behind her, an anime coastal road, a bright blue sea, and simple stylised palm trees stream by quickly from front to back, all drawn in <Subject 2> like her. Wind from the half-open window lifts strands of her black hair. She glances at the camera, smiles, and looks back at the road. The camera is fixed to the car and moves with it.

overall_soundscape:
A steady engine hum, tyres rolling on asphalt, and wind rushing through the half-open window.

non_diegetic_music:
N/A
""",
# 9 -- the woman in Picture 1 drinks coffee from a cup
"""
subject_definitions:
<Subject 1> is the anime-styled young woman in <Picture 1>, with long straight hair that is black at the roots and fades to blonde toward the ends, side-swept bangs covering her right eye, a black glossy corset with pink lace-up ribbons and pink lace trim, and a black-and-pink choker.
<Subject 2> is the 3D anime CG render style of <Picture 1>, applied to the whole frame -- the woman, the environment, every prop and the light: cel-shaded toon shading with soft stylised shadows, smooth flawless skin with no pores or skin texture, large expressive anime eyes, glossy clean highlights on hair and clothing, and clean stylised anime backgrounds.

summary:
[reference generation] <Subject 1> sits at a café table, lifts a cup of coffee, and takes a sip, testing a small object and hand-to-mouth movement. The café and the cup are drawn in <Subject 2> as well.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, two-tone hair, bangs, corset, and choker from <Picture 1> are retained.
<Subject 2> (appears in [Shot 1]): fully_preserved - the 3D anime CG render style of <Picture 1> covers every frame, the café, the table and the cup as much as the woman; nothing turns live-action or photorealistic.

detailed_description:
The whole video is a stylised 3D anime CG animation in <Subject 2>, not live-action footage and not photorealistic, with soft morning light from a café window.
[Shot 1] A medium close-up shows <Subject 1>, the anime-styled young woman with long hair that is black at the roots and blonde toward the ends, side-swept bangs over her right eye, a black glossy corset with pink lace trim, and a black-and-pink choker, sitting at a small round wooden table by the window of an anime café. She is the only person in the frame. A white cup of coffee on a saucer sits in front of her, drawn in <Subject 2> with a clean glossy highlight and a few soft stylised wisps of steam. She lifts the cup by its handle with her right hand, brings it to her lips, takes a small sip, and lowers it back onto the saucer, then smiles with satisfaction. Her fingers hold the handle firmly and the cup keeps its shape. The camera stays still.

overall_soundscape:
Soft café chatter in the background, the clink of the cup on the saucer, and a quiet sip.

non_diegetic_music:
N/A
""",
# 10 -- the two women walk toward each other and shake hands
"""
subject_definitions:
<Subject 1> is the anime-styled young woman in <Picture 1>, with long straight hair that is black at the roots and fades to blonde toward the ends, side-swept bangs covering her right eye, a black glossy corset with pink lace-up ribbons and pink lace trim, and a black-and-pink choker.
<Subject 2> is the anime-styled young woman in <Picture 2>, with long straight black hair, dark gothic eye makeup and dark lipstick, gold hoop earrings, a black choker, a black off-shoulder cropped top, and a colourful floral tattoo sleeve on her left arm.
<Subject 3> is the 3D anime CG render style of <Picture 1> and <Picture 2>, applied to the whole frame -- both women, the environment, every prop and the light: cel-shaded toon shading with soft stylised shadows, smooth flawless skin with no pores or skin texture, large expressive anime eyes, glossy clean highlights on hair and clothing, and clean stylised anime backgrounds.

summary:
[reference generation] In a sunny park, <Subject 1> and <Subject 2> walk toward each other along a path and shake hands, testing whether two referenced people stay apart without swapping faces, hair, or outfits. The whole video stays in <Subject 3>.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, two-tone hair, bangs, corset, and choker from <Picture 1> are retained, and none of them pass to <Subject 2>.
<Subject 2> (appears in [Shot 1]): fully_preserved - her face, black hair, gothic makeup, earrings, choker, cropped top, and arm tattoo from <Picture 2> are retained, and none of them pass to <Subject 1>.
<Subject 3> (appears in [Shot 1]): fully_preserved - the 3D anime CG render style of the pictures covers every frame, the park as much as the two women; nothing turns live-action or photorealistic.

detailed_description:
The whole video is a stylised 3D anime CG animation in <Subject 3>, not live-action footage and not photorealistic, with bright late-morning sunlight.
[Shot 1] A wide shot shows an anime city park with a smooth paved path, tall rounded trees, and bright green grass, all drawn in <Subject 3>. <Subject 1>, the anime-styled young woman with two-tone hair that is black at the roots and blonde toward the ends, bangs over her right eye, and a black glossy corset with pink lace trim, walks in from the left. At the same time <Subject 2>, the anime-styled young woman with long straight black hair, dark gothic makeup, gold hoop earrings, a black off-shoulder cropped top, and a floral tattoo sleeve on her left arm, walks in from the right. They meet in the middle of the path, smile, and shake right hands twice. <Subject 1> stays on the left and <Subject 2> stays on the right the whole time. The camera pushes in with small amplitude at slow speed to a medium two-shot.

overall_soundscape:
Birdsong, a light breeze in the leaves, and soft footsteps on the path.

non_diegetic_music:
N/A
""",
# 11 -- the two women hug
"""
subject_definitions:
<Subject 1> is the anime-styled young woman in <Picture 1>, with long straight hair that is black at the roots and fades to blonde toward the ends, side-swept bangs covering her right eye, a black glossy corset with pink lace-up ribbons and pink lace trim, and a black-and-pink choker.
<Subject 2> is the anime-styled young woman in <Picture 2>, with long straight black hair, dark gothic eye makeup and dark lipstick, gold hoop earrings, a black choker, a black off-shoulder cropped top, and a colourful floral tattoo sleeve on her left arm.
<Subject 3> is the 3D anime CG render style of <Picture 1> and <Picture 2>, applied to the whole frame -- both women, the environment, every prop and the light: cel-shaded toon shading with soft stylised shadows, smooth flawless skin with no pores or skin texture, large expressive anime eyes, glossy clean highlights on hair and clothing, and clean stylised anime backgrounds.

summary:
[reference generation] <Subject 1> and <Subject 2> step toward each other and hug in a bright living room, testing close body contact between two referenced people without their features merging. The whole video stays in <Subject 3>.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, two-tone hair, bangs, corset, and choker from <Picture 1> are retained through the hug.
<Subject 2> (appears in [Shot 1]): fully_preserved - her face, black hair, gothic makeup, earrings, choker, cropped top, and arm tattoo from <Picture 2> are retained through the hug.
<Subject 3> (appears in [Shot 1]): fully_preserved - the 3D anime CG render style of the pictures covers every frame, the living room as much as the two women; nothing turns live-action or photorealistic.

detailed_description:
The whole video is a stylised 3D anime CG animation in <Subject 3>, not live-action footage and not photorealistic, with warm, soft daylight.
[Shot 1] A medium shot shows a bright anime living room with a simple beige sofa and large windows, drawn in <Subject 3>. <Subject 1>, the anime-styled young woman with two-tone hair that is black at the roots and blonde toward the ends, bangs over her right eye, and a black glossy corset with pink lace trim, stands on the left. <Subject 2>, the anime-styled young woman with long straight black hair, dark gothic makeup, gold hoop earrings, a black off-shoulder cropped top, and a floral tattoo sleeve on her left arm, stands on the right. They smile, step toward each other, and wrap their arms around each other in a warm hug. <Subject 2>'s tattooed left arm rests across <Subject 1>'s back, and <Subject 1>'s blonde hair ends fall over <Subject 2>'s shoulder. They hold the hug, eyes closed, smiling. The camera stays still.

overall_soundscape:
Quiet room tone, the rustle of clothing, and a soft happy sigh during the hug.

non_diegetic_music:
N/A
""",
# 12 -- one woman asks, the other answers: two voices, two short Turkish lines
"""
subject_definitions:
<Subject 1> is the anime-styled young woman in <Picture 1>, with long straight hair that is black at the roots and fades to blonde toward the ends, side-swept bangs covering her right eye, a black glossy corset with pink lace-up ribbons and pink lace trim, and a black-and-pink choker.
<Subject 2> is the anime-styled young woman in <Picture 2>, with long straight black hair, dark gothic eye makeup and dark lipstick, gold hoop earrings, a black choker, a black off-shoulder cropped top, and a colourful floral tattoo sleeve on her left arm.
<Subject 3> is the 3D anime CG render style of <Picture 1> and <Picture 2>, applied to the whole frame -- both women, the environment, every prop and the light: cel-shaded toon shading with soft stylised shadows, smooth flawless skin with no pores or skin texture, large expressive anime eyes, glossy clean highlights on hair and clothing, and clean stylised anime backgrounds.

summary:
[reference generation] <Subject 1> and <Subject 2> sit facing each other at a café table and exchange two short lines in Turkish, testing two distinct voices and the right mouth moving for each line. The whole video stays in <Subject 3>.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, two-tone hair, bangs, corset, and choker from <Picture 1> are retained.
<Subject 2> (appears in [Shot 1]): fully_preserved - her face, black hair, gothic makeup, earrings, choker, cropped top, and arm tattoo from <Picture 2> are retained.
<Subject 3> (appears in [Shot 1]): fully_preserved - the 3D anime CG render style of the pictures covers every frame, the café as much as the two women; nothing turns live-action or photorealistic.

detailed_description:
The whole video is a stylised 3D anime CG animation in <Subject 3>, not live-action footage and not photorealistic, with soft daylight from a café window.
[Shot 1] A medium two-shot in profile shows a small table by the window of an anime café, drawn in <Subject 3>. <Subject 1> (S1), the anime-styled young woman with two-tone hair that is black at the roots and blonde toward the ends, bangs over her right eye, and a black glossy corset with pink lace trim, sits on the left. <Subject 2> (S2), the anime-styled young woman with long straight black hair, dark gothic makeup, gold hoop earrings, a black off-shoulder cropped top, and a floral tattoo sleeve on her left arm, sits on the right. <Subject 1> (S1) leans in and asks in a soft, sweet young female voice, <d>[Turkish] Nasılsın bugün?</d> <Subject 2> (S2) keeps her mouth closed while <Subject 1> speaks, then answers in a lower, husky young female voice with a relaxed tone, <d>[Turkish] Çok iyiyim, ya sen?</d> while <Subject 1> listens and smiles. The camera stays still.

overall_soundscape:
Soft café chatter and the faint clink of cups in the background.

non_diegetic_music:
N/A
""",
# 13 -- the two women box in a ring
"""
subject_definitions:
<Subject 1> is the anime-styled young woman in <Picture 1>, with long straight hair that is black at the roots and fades to blonde toward the ends, side-swept bangs covering her right eye, a black glossy corset with pink lace-up ribbons and pink lace trim, and a black-and-pink choker.
<Subject 2> is the anime-styled young woman in <Picture 2>, with long straight black hair, dark gothic eye makeup and dark lipstick, gold hoop earrings, a black choker, a black off-shoulder cropped top, and a colourful floral tattoo sleeve on her left arm.
<Subject 3> is the 3D anime CG render style of <Picture 1> and <Picture 2>, applied to the whole frame -- both women, the environment, every prop and the light: cel-shaded toon shading with soft stylised shadows, smooth flawless skin with no pores or skin texture, large expressive anime eyes, glossy clean highlights on hair and clothing, and clean stylised anime backgrounds.

summary:
[reference generation] <Subject 1> and <Subject 2> box each other in a boxing ring, trading fast punches and blocks, testing fast movement, impacts, and whether limbs and identities hold together. The whole video stays in <Subject 3>.

retention_analysis:
<Subject 1> (appears in [Shot 1]): partially_preserved - her face, two-tone hair, bangs, corset, and choker from <Picture 1> are retained, with red boxing gloves added.
<Subject 2> (appears in [Shot 1]): partially_preserved - her face, black hair, gothic makeup, cropped top, and arm tattoo from <Picture 2> are retained, with blue boxing gloves added.
<Subject 3> (appears in [Shot 1]): fully_preserved - the 3D anime CG render style of the pictures covers every frame, the ring, the gloves and the arena as much as the two women; nothing turns live-action or photorealistic.

detailed_description:
The whole video is a stylised 3D anime CG animation in <Subject 3>, not live-action footage and not photorealistic, with bright white spotlights over the ring and a dark arena around it.
[Shot 1] A medium-wide shot at ring level shows an anime boxing ring with red ropes, drawn in <Subject 3> with clean shapes and glossy highlights. <Subject 1>, the anime-styled young woman with two-tone hair that is black at the roots and blonde toward the ends, bangs over her right eye, a black glossy corset with pink lace trim, and red boxing gloves, stands on the left in a fighting stance. <Subject 2>, the anime-styled young woman with long straight black hair, dark gothic makeup, a black off-shoulder cropped top, a floral tattoo sleeve on her left arm, and blue boxing gloves, stands on the right in a fighting stance. They circle once, then <Subject 1> throws two quick jabs that <Subject 2> blocks with her gloves, and <Subject 2> answers with a right hook that <Subject 1> ducks under. Their feet shuffle fast on the canvas and their hair swings with every move. The camera trucks with medium amplitude at fast speed, keeping both fighters in frame.

overall_soundscape:
Gloves thud against gloves, feet squeak and shuffle on the canvas, the ropes creak, and a crowd roars in the dark arena.

non_diegetic_music:
N/A
""",
# 14 -- the woman in Picture 2 runs and jumps over a puddle
"""
subject_definitions:
<Subject 1> is the anime-styled young woman in <Picture 2>, with long straight black hair, dark gothic eye makeup and dark lipstick, gold hoop earrings, a black choker, a black off-shoulder cropped top, and a colourful floral tattoo sleeve on her left arm.
<Subject 2> is the 3D anime CG render style of <Picture 2>, applied to the whole frame -- the woman, the environment, every prop and the light: cel-shaded toon shading with soft stylised shadows, smooth flawless skin with no pores or skin texture, large expressive anime eyes, glossy clean highlights on hair and clothing, and clean stylised anime backgrounds.

summary:
[reference generation] <Subject 1> runs along a park path and leaps over a puddle, testing identity and anatomy at speed. The park is drawn in <Subject 2> as well.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, black hair, gothic makeup, earrings, choker, cropped top, and arm tattoo from <Picture 2> are retained while she runs and jumps.
<Subject 2> (appears in [Shot 1]): fully_preserved - the 3D anime CG render style of <Picture 2> covers every frame, the park and the puddle as much as the woman; nothing turns live-action or photorealistic.

detailed_description:
The whole video is a stylised 3D anime CG animation in <Subject 2>, not live-action footage and not photorealistic, with bright morning sunlight after rain.
[Shot 1] A wide side-on shot shows an anime park path still wet from rain, with a wide puddle in the middle, the path, the grass and the trees drawn in <Subject 2>. <Subject 1>, the anime-styled young woman with long straight black hair, dark gothic makeup, gold hoop earrings, a black choker, a black off-shoulder cropped top, and a floral tattoo sleeve on her left arm, runs in from the left at full speed. She is the only person in the frame. Her arms pump, her long black hair streams behind her, and her feet strike the wet path. At the puddle she pushes off with one foot, leaps over it with her legs stretched in a wide stride, lands cleanly on the far side, and keeps running out of frame to the right, laughing. Her clean stylised reflection flashes across the puddle as she flies over it. The camera pans right with medium amplitude at fast speed to follow her.

overall_soundscape:
Quick footsteps slapping on the wet path, her breathing, a short laugh, and birdsong in the park.

non_diegetic_music:
N/A
""",
# 15 -- the woman in Picture 1 dances, with a full spin
"""
subject_definitions:
<Subject 1> is the anime-styled young woman in <Picture 1>, with long straight hair that is black at the roots and fades to blonde toward the ends, side-swept bangs covering her right eye, a black glossy corset with pink lace-up ribbons and pink lace trim, and a black-and-pink choker.
<Subject 2> is the 3D anime CG render style of <Picture 1>, applied to the whole frame -- the woman, the environment, every prop and the light: cel-shaded toon shading with soft stylised shadows, smooth flawless skin with no pores or skin texture, large expressive anime eyes, glossy clean highlights on hair and clothing, and clean stylised anime backgrounds.

summary:
[reference generation] <Subject 1> dances to upbeat music on a stage and makes one full spin, testing whether her face comes back unchanged after turning away. The stage is drawn in <Subject 2> as well.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, two-tone hair, bangs, corset, and choker from <Picture 1> are retained before, during, and after the spin.
<Subject 2> (appears in [Shot 1]): fully_preserved - the 3D anime CG render style of <Picture 1> covers every frame, the stage and its lights as much as the woman; nothing turns live-action or photorealistic.

detailed_description:
The whole video is a stylised 3D anime CG animation in <Subject 2>, not live-action footage and not photorealistic, with coloured stage lights in pink and purple.
[Shot 1] A full shot shows a small dark anime stage with pink and purple spotlight beams, drawn in <Subject 2> as clean glowing shapes. <Subject 1>, the anime-styled young woman with long hair that is black at the roots and blonde toward the ends, side-swept bangs over her right eye, a black glossy corset with pink lace trim, and a black-and-pink choker, dances in the centre. She is the only person in the frame. She sways her hips and moves her arms to the beat, then rises onto the balls of her feet and makes one full, fast spin, her two-tone hair fanning out around her. She lands facing the camera again, strikes a pose with one hand on her hip, and smiles, her face the same as before the spin. The camera stays still.

overall_soundscape:
Her heels tap on the wooden stage floor in time with the beat.

non_diegetic_music:
An upbeat electronic pop track with a punchy kick drum and bright synths plays at a fast dance tempo, loud and energetic throughout.
""",
# 17 -- the woman in Picture 1 in a different outfit: a winter coat in the snow
"""
subject_definitions:
<Subject 1> is the anime-styled young woman in <Picture 1>, with long straight hair that is black at the roots and fades to blonde toward the ends, side-swept bangs covering her right eye.
<Subject 2> is the 3D anime CG render style of <Picture 1>, applied to the whole frame -- the woman, the environment, every prop and the light: cel-shaded toon shading with soft stylised shadows, smooth flawless skin with no pores or skin texture, large expressive anime eyes, glossy clean highlights on hair and clothing, and clean stylised anime backgrounds.

summary:
[reference generation] <Subject 1> walks down a snowy street in a long winter coat instead of her corset, testing whether the model keeps her face and hair while changing her outfit. The street and the new coat are drawn in <Subject 2> as well.

retention_analysis:
<Subject 1> (appears in [Shot 1]): partially_preserved - her face, two-tone hair, and bangs from <Picture 1> are retained, while her corset and choker are replaced with a long cream wool winter coat and a red knitted scarf.
<Subject 2> (appears in [Shot 1]): fully_preserved - the 3D anime CG render style of <Picture 1> covers every frame, the snowy street and the new coat as much as the woman; nothing turns live-action or photorealistic.

detailed_description:
The whole video is a stylised 3D anime CG animation in <Subject 2>, not live-action footage and not photorealistic, with soft grey winter daylight.
[Shot 1] A medium shot shows a quiet anime old-town street covered in fresh snow, with simple lamp posts and shop windows glowing warm yellow, all drawn in <Subject 2>. <Subject 1>, the anime-styled young woman with long hair that is black at the roots and blonde toward the ends and side-swept bangs over her right eye, walks toward the camera wearing a long cream wool winter coat buttoned up to the neck, a red knitted scarf, and black gloves, the coat and scarf drawn with the same clean toon shading as her face. She is the only person in the frame. Stylised snowflakes fall slowly and settle on her hair and shoulders, and her breath makes small white puffs in the cold air. She pulls the scarf up a little with one gloved hand and smiles at the camera. The camera pulls back with small amplitude at slow speed, keeping her in a medium shot.

overall_soundscape:
Soft crunching footsteps in fresh snow, a light cold wind, and a distant church bell.

non_diegetic_music:
N/A
""",
# 16 -- the woman in Picture 2 by a window: the same scene twice, in the pool's own 3D anime style here...
"""
subject_definitions:
<Subject 1> is the anime-styled young woman in <Picture 2>, with long straight black hair, dark gothic eye makeup and dark lipstick, gold hoop earrings, a black choker, a black off-shoulder cropped top, and a colourful floral tattoo sleeve on her left arm.
<Subject 2> is the 3D anime CG render style of <Picture 2>, applied to the whole frame -- the woman, the environment, every prop and the light: cel-shaded toon shading with soft stylised shadows, smooth flawless skin with no pores or skin texture, large expressive anime eyes, glossy clean highlights on hair and clothing, and clean stylised anime backgrounds.

summary:
[reference generation] <Subject 1> stands by a window in a bright white apartment hallway, tucks her hair behind her ear, and smiles at the camera, keeping the 3D anime CG style of <Picture 2>. The same scene follows in flat 2D animation, for a side-by-side comparison.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, black hair, gothic makeup, earrings, choker, cropped top, and arm tattoo from <Picture 2> are retained.
<Subject 2> (appears in [Shot 1]): fully_preserved - the 3D anime CG render style of <Picture 2> covers every frame, the hallway and the window as much as the woman; nothing turns live-action or photorealistic.

detailed_description:
The whole video is a stylised 3D anime CG animation in <Subject 2>, not live-action footage and not photorealistic, with bright, soft window light.
[Shot 1] A medium close-up shows <Subject 1>, the anime-styled young woman with long straight black hair, dark gothic eye makeup and dark lipstick, gold hoop earrings, a black choker, a black off-shoulder cropped top, and a colourful floral tattoo sleeve on her left arm, standing by a window in a bright white anime apartment hallway, the walls and the window drawn in <Subject 2> with clean, smooth surfaces. She is the only person in the frame. She tucks a strand of black hair behind her ear with her tattooed left hand, looks into the lens, and gives a small smile. The camera pushes in with small amplitude at slow speed.

overall_soundscape:
Quiet apartment room tone with faint traffic outside the window.

non_diegetic_music:
N/A
""",
# 16 -- ...and in flat 2D cel animation here, a style the pool does not show
"""
subject_definitions:
<Subject 1> is the young woman in <Picture 2>, with long straight black hair, dark gothic eye makeup and dark lipstick, gold hoop earrings, a black choker, a black off-shoulder cropped top, and a colourful floral tattoo sleeve on her left arm.

summary:
[reference generation] <Subject 1> stands by a window in a bright white apartment hallway, tucks her hair behind her ear, and smiles at the camera, redrawn as flat 2D hand-drawn cel animation instead of the 3D anime CG look of <Picture 2>, testing whether the model can move the style away from realism while keeping who she is.

retention_analysis:
<Subject 1> (appears in [Shot 1]): partially_preserved - her facial features, black hair, gothic makeup, earrings, choker, cropped top, and arm tattoo from <Picture 2> are retained, while the 3D anime CG look is replaced with flat 2D cel animation.

detailed_description:
The whole video is a flat 2D hand-drawn anime cel animation, like a classic television anime series: bold clean black outlines, flat colour fills, one-tone cel shadows, simple highlights, and flat painted backgrounds, with no 3D shading, no depth of field, and nothing photorealistic.
[Shot 1] A medium close-up shows <Subject 1>, drawn as a 2D anime character with long straight black hair in flat black shapes, dark gothic eye makeup and dark lipstick, gold hoop earrings, a black choker, a black off-shoulder cropped top, and a colourful floral tattoo sleeve on her left arm drawn in flat colours with clean outlines, standing by a window in a bright white apartment hallway painted as a flat 2D background. She is the only person in the frame. She tucks a strand of black hair behind her ear with her tattooed left hand, looks into the lens, and gives a small smile. The camera pushes in with small amplitude at slow speed.

overall_soundscape:
Quiet apartment room tone with faint traffic outside the window.

non_diegetic_music:
N/A
""",
]
