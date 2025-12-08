import torchaudio as ta
import torch
from chatterbox.tts import ChatterboxTTS
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

# Automatically detect the best available device
if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"

print(f"Using device: {device}")

model = ChatterboxTTS.from_pretrained(device=device)

text = """Good morning everyone! Welcome to CS101 – Introduction to Artificial Intelligence.
I’m Professor [Your Name], this is our head TA [Name], and we have a great team ready to help you all semester.
Quick show of hands: How many of you used ChatGPT, Claude, Grok, Gemini, or Copilot this morning?
(Wait for hands)
Amazing. That means every one of you has already used state-of-the-art AI today.
This course is about pulling back the curtain: how that “magic” actually works, where it breaks, and why it sometimes feels smarter than it really is.
Fast syllabus rundown: 14 weeks, Python-based assignments, two exams, one fun final project. Everything lives on the course website. If you’ve never coded before — don’t worry, we truly start from zero.
Let’s warm up with a quick live poll (phones out!):
Which of these counts as “real AI” in your mind right now?

Netflix recommendations
Tesla Full Self-Driving
Google Search
A basic calculator
ChatGPT writing essays
A Roomba
Vote now!
(Pause for votes, then show results)
Keep those answers in your head — we’ll circle back.

So… what actually IS artificial intelligence?
The textbook gives us four classic definitions (show the famous 2×2 table):

Thinking humanly → cognitive modeling
Thinking rationally → laws of thought, logic
Acting humanly → the Turing Test
Acting rationally → rational agents (← this is the one we will use all semester)

We focus on rational agents because it’s practical, measurable, and it’s what powers almost every useful AI system you interact with.
Quick (and fun) history lightning round — buckle up.
1950 – Alan Turing asks “Can machines think?”
1956 – Dartmouth conference, the official birth of AI. They thought they’d crack it in one summer.
1960s–70s – Early excitement, then the first “AI winter” when funding dried up.
1980s – Expert systems boom, then the second AI winter.
1997 – Deep Blue beats Garry Kasparov.
2011 – IBM Watson wins Jeopardy!
2016 – AlphaGo shocks the world with Move 37 against Lee Sedol.
2022 – ChatGPT goes public.
2025 – You are here, living in the biggest AI explosion ever.
The field has died twice and come back stronger both times. Never count AI out.
Back to rational agents. Every AI system we study this semester can be described with four letters: PEAS
P – Performance measure
E – Environment
A – Actuators
S – Sensors
Example: Roomba vacuum
P → cleanliness, battery life, noise
E → your messy living room
A → wheels, suction, bumper
S → dirt sensor, cliff sensor, bump sensor
Let’s design one together right now.
Live on the whiteboard: PEAS for an “AI teaching assistant” (you shout ideas, I write them down).
Your turn — in pairs, pick one and write its PEAS in 90 seconds:

Self-driving car
Spam filter
Stock-trading bot
Medical diagnosis system
Go!
(Let a couple pairs share quickly)

You just did real AI systems design. That’s literally how companies like OpenAI, Waymo, and DeepMind start every project.
One teaser before we go: Wednesday we’ll dive deep into the Turing Test… and why almost no serious AI researcher today believes passing it proves genuine intelligence."""
#wav = model.generate(text)
#ta.save("test-1.wav", wav, model.sr)

#multilingual_model = ChatterboxMultilingualTTS.from_pretrained(device=device)
#text = "Bonjour, comment ça va? Ceci est le modèle de synthèse vocale multilingue Chatterbox, il prend en charge 23 langues."
#wav = multilingual_model.generate(text, language_id="fr")
#ta.save("test-2.wav", wav, multilingual_model.sr)


# If you want to synthesize with a different voice, specify the audio prompt
AUDIO_PROMPT_PATH = "chris_hansen_sample.wav"
wav = model.generate(text, audio_prompt_path=AUDIO_PROMPT_PATH)
ta.save("test-3.wav", wav, model.sr)
