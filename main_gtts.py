from epub import parse_html_to_dict, extract_chapters_from_epub, clean_string
from audio import generate_audio_gtts
from moviepy.editor import TextClip, concatenate_videoclips, AudioFileClip, ImageClip, CompositeVideoClip
import os
from tqdm import tqdm
import re

audio_folder = "audios"

def get_background_picture(name):
    for fmt in ("jpg", "png"):
        background_image_path = 'backgrounds/{}.{}'.format(name, fmt)  # Path to your background image
        if os.path.exists(background_image_path):
            return background_image_path
    return ""

def create_audio_and_text_clips(name, chapter_index, sentences, background_image_path):
    """Creates and returns a list of TextClips and AudioFileClips for each sentence."""
    clips = []

    # Create an ImageClip for the background
    background_image = ImageClip(background_image_path).resize(height=720)

    print(sentences)

    for idx in tqdm(range(len(sentences))):
        sentence = clean_string(sentences[idx])
        # Generate audio for the sentence
        file_name = "{}_C{}S{}".format(name, chapter_index, idx+1)
        audio_file = generate_audio_gtts(file_name, sentence, speed=1.1)

        # Create an AudioFileClip from the adjusted audio
        audio_clip = AudioFileClip(audio_file)

        # Resize the background image while maintaining the aspect ratio
        background_image = background_image.set_duration(audio_clip.duration)

        # Create a TextClip with the same duration as the audio
        fontsize = 50 if idx == 0 else 30
        text_clip = TextClip(sentence, fontsize=fontsize, color='white', size=(1220, 720), method='caption')
        text_clip = text_clip.set_duration(audio_clip.duration)

        # Position text in the center over the background
        text_clip = text_clip.set_position('center')

        # Create a composite video clip with the background and text overlay
        video_clip = CompositeVideoClip([background_image.set_duration(audio_clip.duration), text_clip.set_duration(audio_clip.duration)], size=(1280, 720))
        video_clip = video_clip.set_audio(audio_clip)

        clips.append(video_clip)

    return clips

def create_intro_clip(book_data, background_image_path, tome_index=0):
    """Creates an introductory clip with the book title, author, and year."""
    intro_text = "{}\n\n{}\n\n{}".format(book_data["title"], book_data["author"], "Volume {}".format(tome_index))
    intro_audio_text = "{} by {}, Volume {}".format(book_data["title"], book_data["author"], tome_index)

    # Generate audio for the introduction
    audio_file =  "{}_intro.mp3".format(book_data["id"])

    sped_up_audio_file = generate_audio_gtts(audio_file, intro_audio_text)

    # Load the audio file
    intro_audio_clip = AudioFileClip(sped_up_audio_file)

    # Create a TextClip for the introduction
    text_clip = TextClip(intro_text, fontsize=60, color='white', size=(1220, 720), method='caption')
    text_clip = text_clip.set_duration(intro_audio_clip.duration)

    # Resize the background image while maintaining the aspect ratio
    background_image = ImageClip(background_image_path).resize(height=720)
    background_image = background_image.set_duration(intro_audio_clip.duration)

    # Position text in the center over the background
    text_clip = text_clip.set_position('center')

    # Create a composite video clip with the background and text overlay
    intro_clip = CompositeVideoClip([background_image.set_duration(intro_audio_clip.duration+1), text_clip.set_duration(intro_audio_clip.duration+1)], size=(1280, 720))
    intro_clip = intro_clip.set_audio(intro_audio_clip)

    return intro_clip

def create_video_from_text_clips(clips, output_path="output_video.mp4", fps=6, threads=4):
    """Concatenates TextClips and writes the final video to a file."""
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_path, fps=fps, threads=threads)

# Main execution
if __name__ == "__main__":
    data = {
        "id": 'the_count_of_monte_cristo',
        "title": 'The Count of Monte Cristo',
        "author": "Alexandre Dumas",
        "year": "1846",
    }

    data = {
        "id": 'up_from_slavery',
        "title": 'Up from Slavery',
        "author": " Booker T. Washington",
        "year": "1901",
    }

    background_image_path = get_background_picture(data["id"])

    # Create the audio folder if it doesn't exist
    os.makedirs(audio_folder, exist_ok=True)

    # Extract chapters from the EPUB
    #book = parse_html_to_dict("books/{}.epub".format(data["id"]))

    chapters = extract_chapters_from_epub("books/{}.epub".format(data["id"]))
    # print("Chapter: {} {}".format(len(book), list(book.keys())))

    # chapter_index = 1
    # for tome_index, (tome, chapters) in enumerate(book.items()):
    #     all_clips = []
    #     intro_clip = create_intro_clip(data, background_image_path, tome_index+1)
    #     all_clips.append(intro_clip)
    #     for chapter_title, sentences in chapters.items():
    #         print(f"Processing tome {tome_index+1} {tome} - chapter {chapter_index}: {chapter_title} {len(sentences)}")

    #         ss = [chapter_title] + sentences[:3]
    #         text_clips = create_audio_and_text_clips(data["id"], chapter_index, ss, background_image_path)
    #         print("Text clips: {}".format(len(text_clips)))
    #         all_clips.extend(text_clips)
    #         chapter_index+=1
    #         if chapter_index == 3:
    #             break
    #     # Create and save the final video for the chapter
    #     create_video_from_text_clips(all_clips, "videos/{}_chapter_{}.mp4".format(data["id"], tome_index+1))  # Output name includes chapter 1
    #     break



    for chapter_index, (chapter_title, sentences) in enumerate(chapters.items()):
        if chapter_index+1 != 17:
            continue

        try:
            all_clips = []
            print(f"Processing chapter {chapter_index+1}: {chapter_title}")
            # Create the intro clip
            if chapter_index == 0:
                intro_clip = create_intro_clip(data, background_image_path)
                all_clips.append(intro_clip)

            print("Sentences: {}".format(len(sentences)))
            sentences = [chapter_title] + sentences[99:]
            text_clips = create_audio_and_text_clips(data["id"], chapter_index+1, sentences, background_image_path)
            print("Text clips: {}".format(len(text_clips)))
            all_clips.extend(text_clips)

            # Create and save the final video for the chapter
            create_video_from_text_clips(all_clips, "videos/{}_chapter_{}.mp4".format(data["id"], chapter_index+1))  # Output name includes chapter 1
        except Exception as err:
            print("chapter {} failed".format(chapter_index+1))
            print(err)
        break
