import streamlit as st
import requests
import json
import uuid

def generate_meme(prompt):
    my_uuid = uuid.uuid4()
    uuid_str = str(my_uuid)

    url = "http://127.0.0.1:8080/generate_meme"
    json_payload = {
        "user_id": uuid_str,
        "prompt": prompt
    }
    payload = json.dumps(json_payload)
    headers = {}

    response = requests.request(
        "POST", 
        url, 
        headers = headers, 
        data = payload)
    return response

def main():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("Meme Machine")
    st.write("Welcome to Meme Machine! Generate your memes seamlessly using my multi-agent architecture.")

    input_prompt = st.text_area(
        label = "Write your idea for a meme",
        max_chars = 300
    )

    if st.button("Generate Meme", use_container_width = True):
        if not input_prompt:
            st.error("Note down your idea for a meme before clicking the button.")
        else:
            with st.spinner("Generating your meme...", show_time = True):
                response = generate_meme(input_prompt)
                if response.status_code == 200:
                    response_data = response.json()
                    st.link_button("Go to  Meme", response_data["meme_url"], use_container_width = True)
                    st.write("Here is the generated meme! In case the posted meme was taken down by the subreddit moderators, you can still view it here.")
                    st.image(response_data["image"])
                else:
                    if response.status_code == 400:
                        st.error("Error: Your idea violates the moderation policy of Meme Machine. Please try again with a different idea.")
                    elif response.status_code == 500:
                        st.error("Error: An internal server error occurred. Please try again later.")

def about():
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.title("About Meme Machine")
    st.write("""
        ### Inspiration
        In a world dominated by internet culture, memes have become one of the most effective tools of communication. But creating a timely, witty, and relevant meme still requires human effort and creativity. I wanted to explore what would happen if we gave that job entirely to AI, no human curation, just agents working together to create and publish humor in real-time. **The Meme Machine** was born out of this curiosity: could AI not only understand what's trending, but also turn that into something funny and safe to share?

        ### What it does
        The Meme Machine is a fully autonomous multi-agent system that:
        - Reviews user-submitted idea to ensure meme is appropriate and does not contain unethical or offensive content.
        - Searches relevent meme template from Imgflip.
        - Uses Google's Gemini API to generate funny caption based on user-submitted meme idea.
        - Composes the meme by combining the meme template and the generated caption.
        - Publishes the meme on to Reddit.

        ### How we built it
        I used Google's Agent Development Kit (ADK) to build a multi-agent workflow where each agent has a specialized role. Each agent handles a single responsibility, and overall workflow is orchestrated by a combination of **ParallelAgent** and **SequentialAgent** that ties everything together. This multi-agent system was developed using:
        - **FastAPI** for serving the multi-agent system.
        - **all-MiniLM-L6-v2** model for sentence embedding.
        - **OpenCV** for image processing.
        - **praw** for posting memes to Reddit.

        ### Challenges we ran into
        - **ADK Orchestration:** Coordinating state between agents in a sequential pipeline using ADK required careful state management.
        - **Content Moderation:** Reviewing the user-submitted idea to ensure ethical use of AI for content generation.
        - **Deployment:** Ensuring the service ran smoothly took several iterations.

        ### Accomplishments that we're proud of
        - Developed a fully working, end-to-end meme generation and publishing system from scratch.
        - Successfully integrated five distinct AI agents into a unified pipeline.
        - Learned and implemented Google's brand-new ADK framework in a real-world use case.

        ### What we learned
        - How to design modular, agent-based architecture using ADK.
        - Best practices for API-based content generation and moderation.
        - How to process and combine data in a creative application.
        - Deployment strategies on cloud platforms.

        ### What's next for The Meme Machine
        - **Instagram & Twitter Support:** Extended publishing capabilities beyond Reddit.
        - **Fine-tuned humor model:** Incorporate reinforcement learning from human feedback to mimic human-like humor.
        - **Content Generation & Management for Content Creators:** Develop an integrated platform that assists content creators by suggesting fresh content ideas, generating structured roadmaps for content production, whether based on creator input or brand-specific promotional requirements, automatically creating the content, providing clear guidance for capturing photos or videos when needed, assembling the final content, and managing publication according to a set schedule.
    """)

if __name__ == "__main__":
    st.sidebar.title("Navigation Sidebar")
    if "page" not in st.session_state:
        st.session_state.page = "main"

    if st.sidebar.button("🤖 Meme Generator", use_container_width = True):
        st.session_state.page = "main"
    if st.sidebar.button("ℹ️ About", use_container_width = True):
        st.session_state.page = "about"

    if st.session_state.page == "main":
        main()
    elif st.session_state.page == "about":
        about()