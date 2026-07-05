import sys
import os
import json
sys.path.append('src')
from search import ResearchMatcher


def save_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def professor_flow(matcher):
    print('[SYSTEM]: Select Mode: (1) Student (2) Professor')
    print('> 2\n')
    print('[AGENT]: Welcome to Professor Mode. I can assist with trend analysis, gap identification, and finding collaboration partners. How can I help you today?')
    print('> What\'s trending in Computer Vision?\n')
    print('[AGENT]: Querying Semantic Scholar for current Computer Vision trends...')
    papers = matcher.search_papers('computer vision')
    print('The dominant trends currently involve a shift toward Vision Transformers (ViTs) and generative diffusion models.')
    print('Top recent papers:')
    for p in papers[:2]:
        print(f"- \"{p['title']}\" - {p.get('year',2024)} - {p.get('citations', 0)} Citations.")
    print('\n> Who works on this in our dept?\n')
    print('[AGENT]: Cross-referencing trends with internal ChromaDB profiles...')
    matches = matcher.find_faculty('computer vision', k=5)
    for m in matches[:3]:
        print(f"- {m['name']} works on {m['areas']} (Closest match).")

    print('\n> Could I collaborate with Dr. {} on generative diffusion for medical imaging? (Assume User is Prof. Rajesh Verma)\n'.format(matches[0]['name']))
    print('[AGENT]: Running Collaboration Synergy Analysis...')
    # Simulate analysis
    print(f"- Your Profile (Prof. Verma): Expert in generative media and diffusion models.")
    target_id = matches[0]['id']
    target = matcher.get_faculty_detail(target_id)
    print(f"- {target.get('name')}'s Profile: {target.get('areas')}")
    collabs = matcher.suggest_collaborators(target_id, k=3)
    print('- Synergy Match: HIGH. Suggested collaborators:')
    for c in collabs:
        print(f"  - {c['name']} ({c['areas']}) - score: {c['score']:.2f}, workload: {c['workload']}")

    print('\n> What are we missing?\n')
    print('[AGENT]: Running Gap Analysis (Trending Research vs. Internal Coverage)...')
    gap = 'Gap: The department currently lacks active research explicitly applying Vision Transformer architectures to resource-constrained environments.'
    print('1. Trend Identified: Vision Transformers (ViTs) for real-time edge deployment.')
    print('2. Internal Coverage: some edge detection and IoT work, but few ViT-focused projects.')
    print('3.', gap)
    print('\nWould you like me to draft an email to propose collaboration? (Yes/No)')
    print('> No, just save the gap analysis to my workspace.\n')
    print('[AGENT]: Confirmed. The gap analysis regarding Vision Transformers has been saved to your workspace.')
    save_file('saved/gaps/vision_transformers_gap.txt', gap)


def student_flow(matcher):
    print('[SYSTEM]: Select Mode: (1) Student (2) Professor')
    print('> 1\n')
    print('[AGENT]: Hello! I can help you find a faculty project guide and brainstorm project ideas. What research area or topic are you interested in?')
    print('> Who works on NLP?\n')
    print('[AGENT]: Searching faculty database for "NLP"...')
    matches = matcher.find_faculty('natural language processing', k=5)
    # pick top 2
    top = matches[:2]
    print('I found {} faculty members matching your interest in Natural Language Processing:'.format(len(top)))
    for i, m in enumerate(top, start=1):
        print(f"{i}. {m['name']} (Match Score: {m['score']*100:.0f}%) - Focus: {m['areas']}")

    print('\n> Tell me about {}\n'.format(top[0]['name']))
    detail = matcher.get_faculty_detail(top[0]['id'])
    print('[AGENT]: Fetching details for {}...'.format(detail.get('name')))
    print(f"- Department: Computer Science and Engineering")
    print(f"- Research Areas: {detail.get('areas')}")
    print(f"- Current Workload: {detail.get('workload')} student projects this semester.")
    print(f"- Bio: {detail.get('profile').splitlines()[-1]}")

    print('\n> What project could I do?\n')
    print('[AGENT]: Based on {}\'s profile and current trends, here are two project ideas:'.format(detail.get('name')))
    ideas = [
        'Low-Resource Language LLM Evaluation: Build a framework to test the accuracy of a small language model on a regional language.',
        'Sentiment Bias Detector: Create a tool that analyzes domain-specific text to identify bias.'
    ]
    for i, it in enumerate(ideas, start=1):
        print(f"{i}. {it}")

    print('\nWould you like me to log your interest in "Low-Resource Language LLM Evaluation" under {} and save this to your profile? (Yes/No)'.format(detail.get('name')))
    print('> Yes\n')
    # save interest
    saved = {'faculty': detail.get('name'), 'project': ideas[0]}
    os.makedirs('saved/interests', exist_ok=True)
    with open('saved/interests/interest_1.json','w',encoding='utf-8') as f:
        json.dump(saved, f, indent=2)
    print('[AGENT]: Confirmed. I have logged your interest in this project with {}.'.format(detail.get('name')))


def main():
    matcher = ResearchMatcher()
    professor_flow(matcher)
    print('\n')
    student_flow(matcher)


if __name__ == '__main__':
    main()
