import sys, traceback
sys.path.append('src')
from search import ResearchMatcher

def main():
    try:
        m = ResearchMatcher()
        print('Loaded matcher, profiles:', len(getattr(m,'profiles', {})))
        matches = m.find_faculty('natural language processing', k=3)
        print('matches:', matches)
        detail = m.get_faculty_detail('faizal_gupta.txt')
        print('detail:', detail)
        collabs = m.suggest_collaborators('faizal_gupta.txt')
        print('collabs:', collabs)
    except Exception as e:
        print('ERROR', e)
        traceback.print_exc()

if __name__ == '__main__':
    main()
