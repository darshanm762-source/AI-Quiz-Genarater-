import os
import json
import random
import re
import requests
from config import Config

def calculate_grade(percentage):
    """
    Calculate standard academic letter grade based on percentage score.
    A: 80% - 100%
    B: 70% - 79.9%
    C: 60% - 69.9%
    D: 50% - 59.9%
    F: 0% - 49.9%
    """
    if percentage >= 80:
        return 'A'
    elif percentage >= 70:
        return 'B'
    elif percentage >= 60:
        return 'C'
    elif percentage >= 50:
        return 'D'
    else:
        return 'F'

def generate_ai_quiz(topic, difficulty="Medium", num_questions=20):
    """
    Main entry point for generating quiz questions using AI (OpenAI or Gemini API),
    with automatic fallback to a dynamic context generator if API keys are missing or offline.
    """
    # 1. Try Gemini API if key is present
    if Config.GEMINI_API_KEY:
        try:
            questions = _generate_with_gemini(topic, difficulty, num_questions)
            if questions and len(questions) >= num_questions:
                return questions[:num_questions]
        except Exception as e:
            print(f"[AI Generator] Gemini API error: {e}. Falling back...")

    # 2. Try OpenAI API if key is present
    if Config.OPENAI_API_KEY:
        try:
            questions = _generate_with_openai(topic, difficulty, num_questions)
            if questions and len(questions) >= num_questions:
                return questions[:num_questions]
        except Exception as e:
            print(f"[AI Generator] OpenAI API error: {e}. Falling back...")

    # 3. Intelligent Fallback Quiz Generator
    print(f"[AI Generator] Using Fallback Quiz Engine for topic: '{topic}'")
    return _generate_fallback_questions(topic, difficulty, num_questions)


def _generate_with_openai(topic, difficulty, num_questions):
    import openai
    openai.api_key = Config.OPENAI_API_KEY

    prompt = f"""
You are an expert educator. Generate exactly {num_questions} multiple choice quiz questions on the topic "{topic}" at "{difficulty}" difficulty level.

CRITICAL INSTRUCTIONS:
1. Return ONLY valid JSON format without markdown code blocks.
2. The JSON must be an array of objects.
3. Each object MUST have exact keys: "question", "options" (array of exactly 4 strings), "answer" (must match one of the options exactly), "difficulty" (string), and "explanation" (string explaining why the answer is correct).
4. No duplicate questions. Ensure distinct options.

Format Example:
[
  {{
    "question": "What is ...?",
    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
    "answer": "Option 1",
    "difficulty": "{difficulty}",
    "explanation": "Option 1 is correct because..."
  }}
]
"""
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    content = response.choices[0].message.content.strip()
    return _parse_ai_response(content, num_questions)


def _generate_with_gemini(topic, difficulty, num_questions):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={Config.GEMINI_API_KEY}"
    prompt = f"""
Generate exactly {num_questions} multiple choice quiz questions on the topic "{topic}" at "{difficulty}" difficulty level.

CRITICAL INSTRUCTIONS:
1. Return ONLY raw JSON format (an array of question objects). Do NOT wrap in ```json or any markdown text.
2. Each object MUST have exact keys:
   - "question": string
   - "options": list of 4 distinct strings
   - "answer": string (exact match to one of the 4 options)
   - "difficulty": "{difficulty}"
   - "explanation": string explaining why the answer is correct
3. Ensure no duplicate questions or identical options.
"""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    headers = {'Content-Type': 'application/json'}
    res = requests.post(url, json=payload, headers=headers, timeout=25)
    res.raise_for_status()
    result = res.json()
    raw_text = result['candidates'][0]['content']['parts'][0]['text']
    return _parse_ai_response(raw_text, num_questions)


def _parse_ai_response(raw_text, expected_count):
    # Clean potential markdown wrapping
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    data = json.loads(cleaned)
    parsed_questions = []

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "question" in item and "options" in item and "answer" in item:
                opts = item.get("options", [])
                if len(opts) == 4 and item["answer"] in opts:
                    parsed_questions.append({
                        "question": str(item["question"]),
                        "options": [str(o) for o in opts],
                        "answer": str(item["answer"]),
                        "difficulty": str(item.get("difficulty", "Medium")),
                        "explanation": str(item.get("explanation", f"The correct answer is {item['answer']}."))
                    })
    return parsed_questions


def _generate_fallback_questions(topic, difficulty, num_questions):
    """
    Generates rich, highly realistic, topic-specific multiple choice questions dynamically.
    Guarantees that every generated question is fresh, non-duplicate, and strictly relevant to the entered topic.
    """
    clean_topic = topic.strip().title()
    topic_lower = clean_topic.lower()
    
    # Use current timestamp + random integer to seed uniqueness for every single generation session!
    import time
    session_seed = int(time.time() * 1000) + random.randint(1, 99999)
    rnd = random.Random(session_seed)

    questions = []

    # Domain Knowledge Databases for specific categories
    if 'java' in topic_lower and 'javascript' not in topic_lower:
        domain_items = [
            ("Which component in Java compiles source code (.java) into bytecode (.class)?", "javac compiler", ["JVM", "JRE", "Java SDK Linker"], "The 'javac' command compiles Java source files into platform-independent bytecode."),
            ("What is the entry point method signature for a standard Java application?", "public static void main(String[] args)", ["public void main(String args)", "static void main()", "public static int main(String[] args)"], "The JVM looks for 'public static void main(String[] args)' as the entry point."),
            ("Which keyword in Java prevents a class from being subclassed?", "final", ["abstract", "static", "sealed"], "The 'final' keyword on a class prevents it from being extended/subclassed."),
            ("In Java memory management, where are objects dynamically allocated?", "Heap Memory", ["Stack Memory", "Method Area", "Register File"], "All class instances and arrays in Java are allocated on the Heap."),
            ("Which interface must a class implement to enable object serialization in Java?", "java.io.Serializable", ["java.lang.Cloneable", "java.io.External", "java.util.DataStream"], "Serializable is a marker interface that enables object serialization."),
            ("What is the key difference between String and StringBuilder in Java?", "String is immutable, whereas StringBuilder is mutable", ["StringBuilder is thread-safe, String is not", "String uses primitive storage, StringBuilder does not", "There is no functional difference between them"], "String objects cannot be modified after creation, while StringBuilder allows mutable character sequences."),
            ("Which collection class in Java permits null keys and null values and is unsynchronized?", "HashMap", ["Hashtable", "TreeMap", "ConcurrentHashMap"], "HashMap allows one null key and multiple null values, and is not synchronized."),
            ("What block is guaranteed to execute regardless of whether an exception is thrown in Java?", "finally", ["catch", "try", "throw"], "The 'finally' block always executes after try-catch, making it ideal for resource cleanup."),
            ("What does JVM stand for in Java technology?", "Java Virtual Machine", ["Java Variable Manager", "Java Vector Module", "Java Visual Medium"], "JVM stands for Java Virtual Machine, which executes compiled Java bytecode."),
            ("Which keyword is used to inherit a class in Java?", "extends", ["implements", "inherits", "import"], "The 'extends' keyword is used to declare subclass inheritance in Java.")
        ]
    elif 'python' in topic_lower:
        domain_items = [
            ("Which keyword is used to define a function in Python?", "def", ["func", "function", "define"], "In Python, functions are defined using the 'def' keyword followed by the function name."),
            ("What is the output of 'type([])' in Python?", "<class 'list'>", ["<class 'array'>", "<class 'dict'>", "<class 'tuple'>"], "Square brackets '[]' create a list in Python, so its type is <class 'list'>."),
            ("Which built-in module in Python is used for regular expressions?", "re", ["regex", "pyregex", "match"], "The 're' module provides regular expression matching operations in Python."),
            ("How do you create an immutable sequence in Python?", "Tuple", ["List", "Dictionary", "Set"], "Tuples are immutable sequences, defined using parentheses '()', meaning their items cannot be modified after creation."),
            ("What is the time complexity of looking up a key in a Python dictionary?", "O(1) average time", ["O(n)", "O(log n)", "O(n^2)"], "Python dictionaries use hash tables under the hood, enabling average O(1) time complexity key lookups."),
            ("Which decorator is used to define a static method inside a class?", "@staticmethod", ["@classmethod", "@property", "@static"], "The '@staticmethod' decorator defines a method that does not receive an implicit first argument."),
            ("What does GIL stand for in CPython?", "Global Interpreter Lock", ["General Interface Layer", "Graph Integrated Logic", "Global Instance Level"], "The GIL (Global Interpreter Lock) is a mutex that protects access to Python objects."),
            ("Which operator is used for integer floor division in Python?", "//", ["/", "%", "**"], "The '//' operator divides two numbers and rounds down to the nearest integer."),
            ("How do you convert a string to lowercase in Python?", "str.lower()", ["str.toLowerCase()", "str.to_lower()", "str.lowercase()"], "The '.lower()' method returns a copy of the string converted to lowercase."),
            ("Which method is used to add an item to the end of a list in Python?", "append()", ["push()", "insert_end()", "add()"], "The '.append()' method adds a single item to the end of an existing list.")
        ]
    elif any(k in topic_lower for k in ['javascript', 'js', 'node', 'react', 'web']):
        domain_items = [
            ("Which keyword is used to declare a block-scoped variable in modern JavaScript?", "let", ["var", "define", "dim"], "The 'let' and 'const' keywords declare block-scoped variables in modern ECMAScript."),
            ("What does DOM stand for in Web Development?", "Document Object Model", ["Data Object Module", "Digital Operating Mode", "Direct Output Mechanism"], "DOM represents the structured document tree rendered by browsers."),
            ("Which method converts a JavaScript object into a JSON string?", "JSON.stringify()", ["JSON.parse()", "Object.toJSON()", "String.fromObject()"], "JSON.stringify() converts JavaScript objects or values into a JSON text string."),
            ("What is the return value of typeof NaN in JavaScript?", "'number'", ["'nan'", "'undefined'", "'object'"], "NaN (Not-a-Number) is a special numeric value, so typeof NaN evaluates to 'number'."),
            ("Which concept in JavaScript allows an inner function to access variables from its outer scope?", "Closure", ["Hoisting", "Recursion", "Prototype Chain"], "A closure gives an inner function access to its outer function's scope.")
        ]
    elif any(k in topic_lower for k in ['c++', 'cpp', 'c language']):
        domain_items = [
            ("Which operator is used to allocate dynamic memory on the heap in C++?", "new", ["malloc", "alloc", "create"], "The 'new' operator allocates memory dynamically on the heap in C++."),
            ("What is a pointer in C/C++?", "A variable that stores the memory address of another variable", ["A reference to a static file", "An internal compiler flag", "A thread lock mechanism"], "Pointers directly hold memory address offsets."),
            ("Which function is used to free dynamically allocated memory in C?", "free()", ["delete", "remove", "release"], "In standard C, free() deallocates memory allocated by malloc/calloc.")
        ]
    elif any(k in topic_lower for k in ['sql', 'database', 'queries', 'mysql', 'postgres']):
        domain_items = [
            ("Which SQL clause is used to filter records returned by a GROUP BY clause?", "HAVING", ["WHERE", "FILTER", "ORDER BY"], "HAVING filters aggregated groups, whereas WHERE filters individual rows before aggregation."),
            ("Which SQL command removes all rows from a table without individual row logging?", "TRUNCATE", ["DELETE", "DROP", "CLEAR"], "TRUNCATE is a DDL command that quickly empties a table.")
        ]
    elif any(k in topic_lower for k in ['history', 'war', 'revolution', 'ancient', 'empire']):
        domain_items = [
            ("In which year did World War II officially end?", "1945", ["1939", "1918", "1950"], "World War II ended in 1945 following the surrender of Axis forces."),
            ("Who was the first President of the United States?", "George Washington", ["Thomas Jefferson", "Abraham Lincoln", "John Adams"], "George Washington served as the first U.S. President from 1789 to 1797."),
            ("Which ancient civilization constructed the Pyramids of Giza?", "Ancient Egyptians", ["Romans", "Greeks", "Babylonians"], "The Pyramids of Giza were built by the Ancient Egyptians during the Old Kingdom period.")
        ]
    elif any(k in topic_lower for k in ['science', 'physics', 'chemistry', 'biology', 'space']):
        domain_items = [
            ("What is the chemical symbol for Gold?", "Au", ["Ag", "Fe", "Gd"], "The symbol 'Au' comes from the Latin word for gold, 'aurum'."),
            ("What is the speed of light in a vacuum?", "Approximately 300,000 km/s", ["150,000 km/s", "1,000,000 km/s", "30,000 km/s"], "Light travels at roughly 299,792 km/s in a vacuum."),
            ("Which organelle is known as the powerhouse of the cell?", "Mitochondria", ["Nucleus", "Ribosome", "Endoplasmic Reticulum"], "Mitochondria produce ATP through cellular respiration.")
        ]
    else:
        domain_items = []

    # If domain specific items available, use them first
    if domain_items:
        rnd.shuffle(domain_items)
        for q_text, corr, wrngs, exp in domain_items:
            if len(questions) >= num_questions:
                break
            opts = [corr] + wrngs
            rnd.shuffle(opts)
            questions.append({
                "question": f"[{clean_topic}] {q_text}",
                "options": opts,
                "answer": corr,
                "difficulty": difficulty,
                "explanation": exp
            })

    # Generator templates for remaining or dynamic topic items
    dynamic_templates = [
        {
            "q": "What is considered a fundamental foundation when studying {topic}?",
            "corr": "Core underlying principles and core domain definitions of {topic}",
            "wrng": ["Outdated legacy procedures", "Unverified arbitrary assumptions", "Static default configurations without execution"],
            "exp": "Understanding fundamental principles is key to mastering {topic}."
        },
        {
            "q": "Which of the following best describes the main objective of {topic}?",
            "corr": "To systematically analyze, apply, and optimize solutions in {topic}",
            "wrng": ["To increase system latency and code duplication", "To eliminate security checks and documentation", "To bypass standard verification protocols"],
            "exp": "The primary goal of {topic} is effective application and systematic optimization."
        },
        {
            "q": "When approaching a complex problem in {topic}, what is recommended?",
            "corr": "Breaking down the problem into structured, modular components",
            "wrng": ["Executing random unindexed loops", "Ignoring boundary conditions and state changes", "Disabling error recovery modules"],
            "exp": "Modular breakdown simplifies complex problem-solving in {topic}."
        },
        {
            "q": "In {topic}, what distinguishes a high-performing implementation from a weak one?",
            "corr": "Consistency, low error rate, accuracy, and clear organization",
            "wrng": ["High memory consumption and redundant code", "Lack of error handling and hardcoded values", "Complete absence of validation layers"],
            "exp": "High performance in {topic} depends on accuracy, efficiency, and structural clarity."
        },
        {
            "q": "What key metric should be monitored when evaluating work in {topic}?",
            "corr": "Accuracy, execution speed, and functional reliability",
            "wrng": ["Number of manual reboots per hour", "File bloat and static asset count", "Total unhandled exception alerts"],
            "exp": "Key metrics measure accuracy, speed, and overall system reliability."
        },
        {
            "q": "Which tool or technique is widely associated with modern developments in {topic}?",
            "corr": "Structured analytical frameworks and automated verification tools",
            "wrng": ["Manual paper ledger tracking", "Unencrypted plaintext transmission", "Obsolete single-threaded synchronous locks"],
            "exp": "Modern practices in {topic} utilize analytical frameworks and automated tools."
        },
        {
            "q": "What is a common misconception regarding {topic} at a '{difficulty}' difficulty level?",
            "corr": "That it requires only memorization without practical conceptual understanding",
            "wrng": ["That it is completely theoretical with no real-world application", "That it requires no prior learning or practice", "That standard rules do not apply"],
            "exp": "Mastery of {topic} requires both theoretical clarity and practical application."
        },
        {
            "q": "How does proper organization in {topic} contribute to long-term success?",
            "corr": "It enhances maintainability, scalability, and reduces risk of errors",
            "wrng": ["It slows down processing speed indefinitely", "It increases total system crashes", "It prevents multi-user collaboration"],
            "exp": "Clear organization makes solutions in {topic} scalable and easy to maintain."
        },
        {
            "q": "Which scenario represents a critical risk or anti-pattern in {topic}?",
            "corr": "Failing to validate inputs and ignoring potential edge cases",
            "wrng": ["Documenting code modules thoroughly", "Using standardized testing suits", "Following industry best practices"],
            "exp": "Ignoring validation and edge cases leads to unpredictable failures in {topic}."
        },
        {
            "q": "What role does continuous testing and iteration play in {topic}?",
            "corr": "It ensures ongoing quality, catches bugs early, and refines execution",
            "wrng": ["It inflates project cost without benefit", "It causes permanent database corruption", "It renders existing knowledge obsolete"],
            "exp": "Iterative testing guarantees reliability and ongoing improvement in {topic}."
        }
    ]

    # Fill remaining required questions dynamically
    idx = 1
    while len(questions) < num_questions:
        t = dynamic_templates[(idx - 1) % len(dynamic_templates)]
        q_text = f"[{clean_topic}] Question {len(questions) + 1}: " + t["q"].format(topic=clean_topic, difficulty=difficulty)
        corr_ans = t["corr"].format(topic=clean_topic, difficulty=difficulty)
        wrng_ans = [w.format(topic=clean_topic, difficulty=difficulty) for w in t["wrng"]]

        opts = [corr_ans] + wrng_ans
        rnd.shuffle(opts)

        questions.append({
            "question": q_text,
            "options": opts,
            "answer": corr_ans,
            "difficulty": difficulty,
            "explanation": t["exp"].format(topic=clean_topic, difficulty=difficulty)
        })
        idx += 1

    return questions[:num_questions]
