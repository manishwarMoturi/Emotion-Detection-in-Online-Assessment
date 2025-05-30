from pymongo import MongoClient

def seed_practice_problems():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['emotion_detection']
    practice_questions = db['practice_questions']

    sample_problems = [
        {
            "problem_number": 1,
            "title": "Sum of Two Numbers",
            "description": "Write a function that returns the sum of two numbers.",
            "difficulty": "easy"
        },
        {
            "problem_number": 2,
            "title": "Find Maximum in List",
            "description": "Write a function that finds the maximum number in a list.",
            "difficulty": "easy"
        },
        {
            "problem_number": 3,
            "title": "Check Palindrome",
            "description": "Write a function to check if a string is a palindrome.",
            "difficulty": "medium"
        },
        {
            "problem_number": 4,
            "title": "Fibonacci Sequence",
            "description": "Write a function to generate the first n Fibonacci numbers.",
            "difficulty": "medium"
        },
        {
            "problem_number": 5,
            "title": "Merge Sort",
            "description": "Implement the merge sort algorithm.",
            "difficulty": "hard"
        },
        {
            "problem_number": 6,
            "title": "Binary Search",
            "description": "Implement binary search on a sorted array.",
            "difficulty": "medium"
        },
        {
            "problem_number": 7,
            "title": "Balanced Parentheses",
            "description": "Check if the parentheses in a string are balanced.",
            "difficulty": "medium"
        },
        {
            "problem_number": 8,
            "title": "Longest Substring Without Repeating Characters",
            "description": "Find the length of the longest substring without repeating characters.",
            "difficulty": "hard"
        },
        {
            "problem_number": 9,
            "title": "Rotate Matrix",
            "description": "Rotate an NxN matrix by 90 degrees clockwise.",
            "difficulty": "hard"
        },
        {
            "problem_number": 10,
            "title": "Two Sum",
            "description": "Find two numbers in an array that add up to a target sum.",
            "difficulty": "easy"
        }
    ]

    # Insert sample problems if collection is empty
    if practice_questions.count_documents({}) == 0:
        practice_questions.insert_many(sample_problems)
        print("Inserted 10 sample practice problems into the database.")
    else:
        print("Practice questions collection already contains data.")

if __name__ == "__main__":
    seed_practice_problems()
