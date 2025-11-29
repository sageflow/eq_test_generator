"""
Section-specific prompts for EQ test generation
Each branch is generated individually to avoid token limits
"""

def get_section_prompts(age: int = 15) -> dict:
    """Get all section prompts with age placeholders replaced"""
    age_str = str(age)
    
    # Determine age category for adaptation
    if 12 <= age <= 14:
        age_category = "12-14"
        emotion_complexity = "clear, basic emotions (happy, sad, angry, scared, surprised)"
        social_scenarios = "simple social scenarios (school, friends, family)"
        tasks = "simple tasks (doing homework, making friends, playing sports)"
        progressions = "simple progressions (sadness → crying, annoyance → anger), obvious causes"
        scenarios = "School conflicts, peer pressure, test anxiety, friendship problems, parental conflicts"
    else:  # 15-18
        age_category = "15-18"
        emotion_complexity = "complex/mixed emotions (ambivalence, nostalgia, resignation, contempt)"
        social_scenarios = "nuanced social situations (romantic relationships, workplace, ethical dilemmas)"
        tasks = "complex tasks (long-term planning, leadership, critical analysis, career decisions)"
        progressions = "complex progressions (disappointment → resentment → bitterness), subtle triggers, mixed emotions"
        scenarios = "Romantic relationships, identity issues, future anxiety, complex moral dilemmas, workplace stress"
    
    prompts = {
        "branch_1": f"""
You are an expert psychometric test designer specializing in emotional intelligence assessment for adolescents. Generate a comprehensive ability-based emotional intelligence (EQ) test section suitable for {age}-year-old test takers following these exact specifications below:

Branch 1: Perceiving Emotions (3 questions)

Skill Measured: Identifying and recognizing emotions in facial expressions, body language, tone, and situations.

Question Types:
- Face/image analysis: Describe facial expressions and ask which emotions are present (provide multiple emotions to rate)
- Scenario-based emotion identification: Present a situation and ask what emotions the person is likely feeling
- Tone/context interpretation: Given a statement or context, identify underlying emotions

Age Adaptation:
- For {age_category} year olds: Use {emotion_complexity}; {social_scenarios}

Expert Consensus Scoring: Rate each emotion option from 1-5 based on how accurately it reflects the presented stimulus
- Most accurate emotion identification = 5 points
- Partially accurate = 3-4 points
- Incorrect/contradictory = 1 point

Output Format Requirements:

1. Branch Number: "Branch 1: Perceiving Emotions"

For each of the 3 questions, provide:

2. Question Number

3. Scenario/Stimulus & Question: Clear description or scenario (age-appropriate for {age} year old). Question based on the scenario.

4. 4-5 Answer Options: Multiple choice options (A, B, C, D, E)

5. Expert Consensus Scores: An Answer-Score mapping, Assign 1-5 points to each option based on correctness 


Example Format:

Branch 1: Perceiving Emotions

Question 1

Scenario & Question: [Age {age}] Sarah walked into the cafeteria and saw her friend group laughing together at a table. When she approached, they suddenly stopped talking and looked at each other. One friend said, "Oh hey, Sarah," in a flat tone. Which emotions is Sarah most likely experiencing in this moment?

Options:
A) Excitement and joy
B) Confusion and hurt
C) Anger and aggression
D) Indifference and calm
E) Mild curiosity

Expert Consensus Scores: A: 1, B: 5, C: 2, D: 1, E: 3

Question 2

Scenario & Question: [Age {age}] Look at the image of the person. Their eyebrows are pulled slightly together and upward, their mouth is turned down at the corners, and they are looking down and away. Which of the following emotions is this person most likely feeling?

Options:
A) Happiness and excitement
B) Disgust and anger
C) Sadness and disappointment
D) Fear and surprise
E) Confidence and pride

Expert Consensus Scores: A: 1, B: 2, C: 5, D: 3, E: 1

Question 3

Scenario & Question: [Age {age}] Alex spent weeks preparing a solo for the school talent show. Right after finishing the performance, the audience is silent for a moment before starting to clap. Alex walks off the stage, takes a deep breath, and says to a friend, "Well, I'm just glad it's over," while avoiding eye contact. Which emotions is Alex most likely experiencing?

Options:
A) Pure relief and satisfaction
B) Disappointment and anxiety about their performance
C) Boredom and indifference
D) Anger towards the audience
E) Pride and excitement for the next opportunity

Expert Consensus Scores: A: 2, B: 5, C: 1, D: 1, E: 3
""",

        "branch_2": f"""
You are an expert psychometric test designer specializing in emotional intelligence assessment for adolescents. Generate a comprehensive ability-based emotional intelligence (EQ) test section suitable for {age}-year-old test takers following these exact specifications below:

Branch 2: Using Emotions to Facilitate Thought (3 questions)

Skill Measured: Understanding which emotions are helpful for specific tasks and using emotions strategically.

Question Types:
- Task-emotion matching: "What emotion would be most helpful for [specific task]?"
- Mood optimization: "If you want to [achieve goal], which emotional state would help most?"
- Emotional leverage: Scenarios where emotions can enhance thinking or problem-solving

Common Tasks to Include:
- Creative brainstorming
- Detail-oriented work
- Making careful decisions
- Connecting with others
- Learning new material

Age Adaptation:
- For {age_category} year olds: Use {tasks}

Expert Consensus Scoring: 
- Most facilitating emotion = 5 points
- Somewhat helpful = 3-4 points
- Neutral/unhelpful = 2 points
- Counterproductive = 1 point

Output Format Requirements:
For each of the 3 questions, provide:

1. Branch Number: "Branch 2: Using Emotions to Facilitate Thought"

For each of the 3 questions, provide:

2. Question Number

3. Scenario/Stimulus & Question: Clear description or scenario (age-appropriate for {age} year old). Question based on the scenario.

4. 4-5 Answer Options: Multiple choice options (A, B, C, D, E)

5. Expert Consensus Scores: An Answer-Score mapping, Assign 1-5 points to each option based on correctness

---

Example Format:

Branch 2: Using Emotions to Facilitate Thought
Question 1

Scenario & Question: [Age {age}] You have a big, open-ended project for a class where you need to come up with a completely original idea and presentation. You are in the initial "brainstorming" phase, trying to generate as many creative possibilities as you can. Which emotional state would be MOST helpful for this specific part of the task?

Options:
A) Calm contentment
B) Anxious worry
C) Playful curiosity
D) Serious skepticism
E) Frustrated determination

Expert Consensus Scores: A: 3, B: 1, C: 5, D: 2, E: 1

Question 2

Scenario & Question: [Age {age}] You are about to proofread your application for a summer program you really want to join. This is your final check for any small spelling, grammar, or formatting errors before you hit "submit." Which emotional state would be MOST helpful for ensuring you catch every detail?

Options:
A) Excited enthusiasm
B) Focused calm
C) Confident pride
D) Playful humor
E) Impatient eagerness

Expert Consensus Scores: A: 2, B: 5, C: 3, D: 1, E: 1

Question 3

Scenario & Question: [Age {age}] You had a minor disagreement with a friend, and there's some lingering tension. You've decided to approach them to talk it out and clear the air. Your goal is to reconnect and understand their perspective. Which emotional approach would be MOST helpful in facilitating this conversation?

Options:
A) Defensive, to protect your own feelings
B) Empathetic and open-minded
C) Apologetic, even if you're not sure what you did wrong
D) Lighthearted, to try and joke about the situation immediately
E) Neutral and unemotional

Expert Consensus Scores: A: 1, B: 5, C: 3, D: 2, E: 2

""",

        "branch_3": f"""
You are an expert psychometric test designer specializing in emotional intelligence assessment for adolescents. Generate a comprehensive ability-based emotional intelligence (EQ) test section suitable for {age}-year-old test takers following these exact specifications below:

Branch 3: Understanding Emotions (3 questions)

Skill Measured: Comprehending how emotions arise, evolve, and combine; understanding emotional cause-and-effect.

Question Types:
- Emotional progression: "If [initial emotion] continues, what emotion might develop next?"
- Cause analysis: "What most likely caused this person to feel [emotion]?"
- Emotional blends: "When someone feels [emotion A] and [emotion B] together, this is called [what]?"
- Intensity scaling: Ordering emotions by intensity (e.g., annoyance → frustration → anger → rage)

Age Adaptation:
- For {age_category} year olds: Use {progressions}

Expert Consensus Scoring: 
- Most accurate progression/cause = 5 points
- Partially correct = 3 points
- Incorrect/illogical = 1 point

Output Format Requirements:

1. Branch Number: "Branch 3: Understanding Emotions"

For each of the 3 questions, provide:

2. Question Number

3. Scenario/Stimulus & Question: Clear description or scenario (age-appropriate for {age} year old). Question based on the scenario.

4. 4-5 Answer Options: Multiple choice options (A, B, C, D, E)

5. Expert Consensus Scores: An Answer-Score mapping, Assign 1-5 points to each option based on correctness 

---

Example Format:

Branch 3: Understanding Emotions
Question 1

Scenario & Question: [Age {age}] Alex worked for weeks on a science fair project, putting in extra hours to make it perfect. When the results were announced, Alex did not even place in the top three. If Alex's initial feeling is one of deep disappointment, what is a LIKELY emotion that might follow if they can't process the initial feeling?

Options:
A) Gratitude for the experience
B) Apathy towards science
C) Renewed motivation to try harder
D) Confusion about the judging
E) Increased confidence

Expert Consensus Scores: A: 1, B: 5, C: 3, D: 2, E: 1

Question 2

Scenario & Question: [Age {age}] Jamie suddenly feels a mix of nervousness and excited anticipation, with a racing heart and butterflies in the stomach. What is the MOST likely cause of this blend of emotions?

Options:
A) Forgetting to do a homework assignment
B) Getting a surprise quiz in a difficult class
C) About to perform a solo in the school concert
D) Hearing a loud, unexpected noise
E) Being assigned extra chores at home

Expert Consensus Scores: A: 2, B: 3, C: 5, D: 1, E: 1

Question 3

Scenario & Question: [Age {age}] Consider the following emotions related to anger. Which sequence shows the most accurate progression from the mildest form to the most intense?

Options:
A) Rage -> Frustration -> Annoyance -> Fury
B) Annoyance -> Frustration -> Anger -> Rage
C) Irritation -> Fury -> Resentment -> Annoyance
D) Frustration -> Annoyance -> Rage -> Anger
E) Anger -> Annoyance -> Fury -> Frustration

Expert Consensus Scores: A: 1, B: 5, C: 2, D: 1, E: 1

""",

        "branch_4": f"""
You are an expert psychometric test designer specializing in emotional intelligence assessment for adolescents. Generate a comprehensive ability-based emotional intelligence (EQ) test section suitable for {age}-year-old test takers following these exact specifications below:

Branch 4: Managing Emotions (3 questions)

Skill Measured: Regulating one's own emotions and managing emotions in relationships effectively.

Question Types:
- Strategy effectiveness: Present a scenario where someone experiences an emotion, then rate various coping strategies
- Interpersonal regulation: How to help someone else manage their emotions
- Self-regulation: Best approaches for managing one's own emotional state in challenging situations

Scenarios Should Include:
- Anxiety/stress management
- Anger/frustration regulation
- Sadness/disappointment coping
- Interpersonal conflict resolution
- Social pressure situations

Age Adaptation:
- For {age_category} year olds: Use scenarios related to {scenarios}

Expert Consensus Scoring: Rate each strategy's effectiveness
- Highly effective (healthy, adaptive, evidence-based) = 5 points
- Moderately effective = 3 points
- Ineffective or counterproductive (avoidance, suppression, aggression) = 1 point

Output Format Requirements:

1. Branch Number: "Branch 4: Managing Emotions"

For each of the 3 questions, provide:

2. Question Number

3. Scenario/Stimulus & Question: Clear description or scenario (age-appropriate for {age} year old). Question based on the scenario.

4. 4-5 Answer Options: Multiple choice options (A, B, C, D, E) representing different coping strategies

5. Expert Consensus Scores: Assign 1-5 points to each option based on effectiveness

---

Example Format:

Branch 4: Managing Emotions
Question 1

Scenario & Question: [Age {age}] Sam has an important final exam in one hour. Sam is feeling extremely anxious, with a racing mind and shaky hands. What is the MOST effective strategy for Sam to use in the next 15 minutes to manage this anxiety and get into a better headspace for the test?

Options:
A) Suppress the feelings and try to think about something else entirely.
B) Find a quiet space to do a few minutes of deep breathing and positive self-talk.
C) Cram as much last-minute information as possible to feel more prepared.
D) Complain to friends about how unfair the test is and how anxious you are.
E) Skip the exam to avoid the uncomfortable feeling entirely.

Expert Consensus Scores: A: 2, B: 5, C: 2, D: 1, E: 1

Question 2

Scenario & Question: [Age {age}] Taylor is furious after a teammate repeatedly dropped the ball during a crucial play, causing their team to lose the championship game. Taylor is about to confront the teammate. What is the MOST effective way for Taylor to manage this anger in the moment?

Options:
A) Yell at the teammate immediately to release the anger.
B) Walk away, cool down for 10 minutes, then discuss what happened calmly.
C) Give the teammate the silent treatment for the rest of the day.
D) Immediately post about the teammate's mistake on social media.
E) Bottle up the anger and pretend everything is fine.

Expert Consensus Scores: A: 1, B: 5, C: 1, D: 1, E: 1

Question 3

Scenario & Question: [Age {age}] Your friend Riley is visibly upset and crying after a fight with their parents. Riley says, "They never listen to me!" What is the MOST effective way for you to help Riley manage their emotions in this situation?

Options:
A) Tell them to calm down and that it's not a big deal.
B) Immediately offer advice on how to fix the problem.
C) Listen quietly, show you are there for them, and validate their feelings.
D) Change the subject to a funny video to distract them.
E) Agree with them and criticize their parents to show you're on their side.

Expert Consensus Scores: A: 1, B: 2, C: 5, D: 2, E: 1

"""
    }
    
    return prompts

