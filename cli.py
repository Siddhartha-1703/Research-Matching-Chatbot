import argparse
import random
import sys
import textwrap
from pathlib import Path

# Ensure the repository root is on sys.path when executing as `py src/cli.py`
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.search import ResearchMatcher
from src.emailer import send_summary_email


def prompt_yes_no(prompt, default=False):
    answer = input(prompt + ' ').strip().lower()
    if not answer:
        return default
    return answer in ('y', 'yes')


def print_header(title):
    print('\n' + '=' * len(title))
    print(title)
    print('=' * len(title))


def summarize_faculty(detail):
    print('--- Faculty Detail ---')
    print(f"Name: {detail.get('name')}")
    print(f"Research Areas: {detail.get('areas')}")
    print(f"Current Workload: {detail.get('workload')} student projects")
    print('Publications:')
    for p in detail.get('publications', []):
        print(' -', p)
    print('\nBio:')
    print(detail.get('profile'))


def suggest_project_ideas(detail):
    area = detail.get('areas', '')
    name = detail.get('name', 'the faculty member')
    ideas = []
    if 'Natural Language Processing' in area:
        ideas.append('Build a low-resource regional language evaluation suite for small language models.')
        ideas.append('Create a sentiment bias detector for domain-specific text.')
    if 'Computer Vision' in area:
        ideas.append('Implement a Vision Transformer prototype for edge deployment.')
        ideas.append('Design a generative medical image enhancement pipeline.')
    if 'Cybersecurity' in area or 'Privacy' in area:
        ideas.append('Evaluate privacy-preserving ML techniques for sensitive data.')
        ideas.append('Build an adversarial robustness toolkit for domain-specific models.')
    if not ideas:
        ideas = [f'Explore applied research in {area} via a small exploratory system.', f'Develop a proof-of-concept study on {area}.']
    print(f"\nHere are some project ideas aligned to {name}:'s research:")
    for i, idea in enumerate(ideas[:3], start=1):
        print(f"{i}. {idea}")
    return ideas


def print_matches(matches, start=0):
    for i, m in enumerate(matches[start:], start=start + 1):
        print(f"{i}. {m['name']} (Match: {m['score']*100:.0f}%)")
        print(f"   Areas: {m['areas']}")


def student_mode(matcher, args):
    print_header('Student Mode')
    print('Welcome! I can help you find a faculty advisor and suggest project ideas.')
    last_matches = []
    last_query = ''
    while True:
        q = input('\nStudent> Enter a research topic, or type "quit": ').strip()
        if not q or q.lower() in ('q', 'quit', 'exit'):
            print('Goodbye!')
            break
        last_query = q
        last_matches = matcher.find_faculty(q, k=5)
        if not last_matches:
            print('I could not find any matching faculty for that topic. Try a different keyword.')
            continue
        print_header('Search Results')
        print_matches(last_matches)

        while True:
            cmd = input('\nStudent> Enter a number for details, "more" for other matches, "idea" for project suggestions, or "new" for a new topic: ').strip().lower()
            if cmd in ('new', 'n'):
                break
            if cmd in ('more', 'another'):
                print('Showing the same results again in case you missed one...')
                print_matches(last_matches)
                continue
            if cmd == 'idea':
                detail = matcher.get_faculty_detail(last_matches[0]['id'])
                suggest_project_ideas(detail)
                continue
            if cmd.isdigit():
                idx = int(cmd) - 1
                if 0 <= idx < len(last_matches):
                    detail = matcher.get_faculty_detail(last_matches[idx]['id'])
                    summarize_faculty(detail)
                    if prompt_yes_no('Would you like project ideas for this faculty? (y/N):'):
                        suggest_project_ideas(detail)
                    if prompt_yes_no(f'Send summary email to {args.recipient}? (y/N):'):
                        send_email(detail, args)
                    if prompt_yes_no('Log your interest in this faculty member? (y/N):'):
                        log_interest(detail, last_query)
                    continue
                print('Please enter a valid number from the list.')
            else:
                print('I did not understand that. Type a number, more, idea, or new.')


def send_email(detail, args):
    subj = f"Faculty match: {detail.get('name')}"
    body_lines = [f"Name: {detail.get('name')}", f"Areas: {detail.get('areas')}", f"Workload: {detail.get('workload')}", '', 'Publications:']
    body_lines += [f"- {p}" for p in detail.get('publications', [])]
    body_lines += ['', 'Full profile:', detail.get('profile')]
    body = '\n'.join(body_lines)
    if args.print_output or args.dry_run:
        print('--- Email Preview ---')
        print('To:', args.recipient)
        print('Subject:', subj)
        print(body)
        if args.log_file:
            try:
                with open(args.log_file, 'a', encoding='utf-8') as lf:
                    lf.write('\n--- EMAIL ---\n')
                    lf.write('To: ' + args.recipient + '\n')
                    lf.write('Subject: ' + subj + '\n')
                    lf.write(body + '\n')
            except Exception as e:
                print('Could not write log file:', e)
    if not args.dry_run:
        result = send_summary_email([args.recipient], subj, body)
        if result.get('ok'):
            print('Summary email sent successfully.')
        else:
            print('Failed to send email:', result.get('error'))


def log_interest(detail, query):
    import json
    import os
    os.makedirs('saved/interests', exist_ok=True)
    data = {'faculty': detail.get('name'), 'query': query, 'project_idea': f"Interest logged for {detail.get('name')}"}
    path = os.path.join('saved', 'interests', f"interest_{detail.get('name').replace(' ', '_')}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f'Interest logged to {path}')


def professor_mode(matcher, args):
    print_header('Professor Mode')
    print('Welcome! I can help with trend analysis, internal matching, and gap spotting.')
    last_trends = []
    last_query = ''
    while True:
        q = input('\nProfessor> Enter a trend query, or type "quit": ').strip()
        if not q or q.lower() in ('q', 'quit', 'exit'):
            print('Goodbye!')
            break
        last_query = q
        last_trends = matcher.search_trends(q)
        print_header('Trend Highlights')
        for i, t in enumerate(last_trends[:5], start=1):
            print(f"{i}. {t}")
        if prompt_yes_no('Would you like to cross-reference these trends with internal faculty? (y/N):'):
            internal_matches = matcher.find_faculty(q, k=5)
            print_header('Internal Matches')
            print_matches(internal_matches)
            if prompt_yes_no('Would you like a collaboration suggestion for the top internal match? (y/N):'):
                detail = matcher.get_faculty_detail(internal_matches[0]['id'])
                print(f"Collaborative opportunity: pair your expertise with {detail.get('name')}.")
                suggest_collaboration(detail)
        if prompt_yes_no('Would you like a gap analysis based on these trends? (y/N):'):
            run_gap_analysis(last_trends, q, matcher)


def suggest_collaboration(detail):
    print('--- Collaboration Summary ---')
    print(f"Name: {detail.get('name')}")
    print(f"Areas: {detail.get('areas')}")
    print('Use this faculty member\'s expertise to complement your own domain knowledge.')


def run_gap_analysis(trends, query, matcher):
    print('--- Gap Analysis ---')
    if 'Vision Transformer' in ' '.join(trends) or 'Vision Transformers' in ' '.join(trends):
        print('Trend Identified: Vision Transformers for real-time edge deployment.')
        print('Internal Coverage: Some edge detection work exists, but ViT-specific edge research is limited.')
        print('Gap: Explore Vision Transformer architectures for resource-constrained environments.')
    else:
        print(f'No strong gap analysis available for "{query}" yet. Try a more specific trend phrase.')


def main():
    parser = argparse.ArgumentParser(description='Research Matching Chatbot (CLI)')
    parser.add_argument('--mode', choices=['student', 'professor'], default='student')
    parser.add_argument('--recipient', default='rendlavishnutej@gmail.com', help='Email recipient for summary emails')
    parser.add_argument('--dry-run', action='store_true', help='Do not actually send emails; print them')
    parser.add_argument('--print-output', action='store_true', help='Always print detailed outputs (including email body)')
    parser.add_argument('--log-file', default='output.log', help='Optional file to append printed outputs')
    parser.add_argument('--version', action='store_true', help='Print version and exit')
    args = parser.parse_args()

    matcher = ResearchMatcher()
    try:
        from src import __version__
        version = __version__
    except Exception:
        version = '0.0.0'
    if args.version:
        print('Research Matching Chatbot version', version)
        return

    if args.mode == 'student':
        student_mode(matcher, args)
    else:
        professor_mode(matcher, args)


if __name__ == '__main__':
    main()
