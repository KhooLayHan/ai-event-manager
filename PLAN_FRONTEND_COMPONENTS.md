# Core Frontend Components

Here is a detailed breakdown of the core UI components for each of the three webpages. This is designed to be a direct set of instructions for your frontend team members, explaining *what* to build and *why* it's important for the demo.

We will use a multi-page app structure in Streamlit, controlled by a sidebar.

## **Core App Structure (The Shell)**

This is the main `src/app.py` file. Its first job is to set up the navigation.

| Component | Streamlit Command | Purpose & Key Details |
| :--- | :--- | :--- |
| **Page Navigation** | `st.sidebar.selectbox()` | Creates the main navigation in the left sidebar. The user will select a page from this dropdown, and your code will show the corresponding content. |
| **App Title** | `st.sidebar.title()` | A clean, persistent title for your project in the sidebar, e.g., "CrowdFlow AI". |
| **Data Persistence** | `st.session_state` | **Crucial Concept:** This is how you will pass data between pages. When the user sets parameters on the "Configuration" page and clicks "Run", you will save those parameters to `st.session_state` before switching to the "Dashboard" page. |

---

### **Page 1: 🌎 Scenario Configuration**

**Goal:** An interactive "control panel" that lets the judges define the problem. It should feel powerful and flexible.

| Component | Streamlit Command | Purpose & Key Details |
| :--- | :--- | :--- |
| **Page Title** | `st.title()` | `CrowdFlow AI: Scenario Setup` |
| **Introductory Text** | `st.markdown()` or `st.info()` | A brief, 1-2 sentence explanation: "Define the event parameters to simulate crowd dynamics and get AI-powered recommendations." |
| **Venue Selector** | `st.selectbox()` | **Label:** `"Select a Venue"`. <br> **Options:** `["Axiata Arena (Concert)", "KLCC (Exhibition)"]`. This shows scalability. For the MVP, only the first option needs to work. |
| **Venue Map Display** | `st.pyplot()` | **Purpose:** To give immediate visual feedback. After a user selects a venue, display a static image of the `venue_map.csv` below the selector. |
| **Simulation Parameters** | `st.slider()` & `st.number_input()` | Create a section for core parameters. Sliders are great for interactivity.<br> - `st.slider("Number of Attendees", min_value=1000, max_value=50000, value=15000, step=1000)`<br> - `st.number_input("Number of Open Gates", min_value=1, max_value=10, value=3)` |
| **The "X-Factor" Input** | `st.radio()` | **Purpose:** To integrate your **Cost-Aware AI** feature directly into the UI.<br> - **Label:** `"Optimization Goal"`<br> - **Options:** `["Maximum Safety", "Balanced Safety & Cost"]` |
| **Run Button** | `st.button()` | **Label:** `"▶️ Run Simulation & Get AI Insights"`. <br> **Action:** When clicked, this will save all the selected settings into `st.session_state` and then programmatically switch the active page to the "Simulation Dashboard". |

---

### **Page 2: 📊 Simulation Dashboard**

**Goal:** The main event. A visually stunning and instantly understandable showcase of your project's impact.

| Component | Streamlit Command | Purpose & Key Details |
| :--- | :--- | :--- |
| **Main Layout** | `st.columns(2)` | This is essential for the **side-by-side "before and after" comparison**. All subsequent components will be placed inside `col1` or `col2`. |
| **Column Headers** | `col1.header()` & `col2.header()` | Clear labels: `"Before AI Optimization"` and `"After AI Optimization"`. |
| **Animation Placeholder** | `col1.empty()` & `col2.empty()` | **Key for animations.** These create empty containers. Your code will then update the content of these containers in a loop to show the agents moving, creating the animation effect. |
| **Key Performance Metrics** | `st.metric()` | **Purpose:** To show the results in a quantifiable way. This is crucial for proving impact.<br> - `col1.metric("Avg. Wait Time", "28 Mins", delta="High Risk", delta_color="inverse")`<br> - `col2.metric("Avg. Wait Time", "7 Mins", delta="-75%", delta_color="normal")` |
| **AI "Thinking" Spinner** | `st.spinner()` | **Purpose:** Improves UX. When the AI is processing, wrap the Bedrock call in a `with st.spinner("🤖 AI is analyzing scenarios..."):` block. |
| **AI Recommendations Display** | `st.info()` or `st.expander()` | **Purpose:** To display the output of your **Explainable AI (XAI)**. Don't just dump text. Format it nicely.<br> - An `st.info()` box with a lightbulb icon (`💡`) is visually appealing.<br> - Use markdown for bullet points: `"**Recommendation:** Open Gate C. **Reason:** ..."` |
| **(Stretch Goal) Comparison Slider** | `image_comparison()` | **Purpose:** The high-impact visual "wow" factor.<br> - This component from `streamlit-image-comparison` will sit below the main columns and display the `before.png` and `after.png` heatmaps. |

---

### **Page 3: 🛠️ About This Project**

**Goal:** Your "meta-page." This is where you directly address the judging criteria and show off your professionalism.

| Component | Streamlit Command | Purpose & Key Details |
| :--- | :--- | :--- |
| **Page Title** | `st.title()` | `About CrowdFlow AI` |
| **Expandable Sections** | `st.expander()` | **Purpose:** To keep the page clean and organized. Create expanders for each section so the user isn't overwhelmed with text. |
| **Architecture Diagram** | `st.image()` | Inside an expander labeled `"System Architecture"`, display your `pitch/architecture.png` file. This shows you've planned your implementation. |
| **Tech Stack Info** | `st.markdown()` | Inside an expander labeled `"Technology Stack"`, list your key tools with bullet points. |
| **Novelty & Impact** | `st.markdown()` | Inside an expander labeled `"Our Winning Strategy (The X-Factors)"`, briefly explain your XAI, Cost-Aware AI, and Interactive UI features. |
| **Team Credits** | `st.markdown()` | Inside an expander labeled `"Meet the Team"`, list your team members and their roles. |
