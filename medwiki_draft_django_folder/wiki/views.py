import os
from django.shortcuts import render
from django.http import Http404

def main_page(request):
    return render(request, 'wiki/main_page.html')

# templates/wiki 경로 설정
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates/wiki')

def render_page(request, page_name):
    try:
        # page_name에서 '-'를 '_'로 변환
        page_name = page_name.replace('-', '_')
        template_name = f'wiki/{page_name}.html'  # 템플릿 파일명 설정
        print(f"Trying to render: {template_name}")  # 디버깅용 출력
        return render(request, template_name)  # 템플릿 렌더링
    except Exception as e:
        raise Http404(f"Error: {str(e)}")
    

def search_results(request):
    query = request.GET.get('q')  # 검색어 가져오기
    related_entries = []  # 관련 항목을 저장할 리스트

    # templates/wiki 디렉토리에서 .html 파일을 읽음 (main_page.html과 search_result.html은 제외)
    html_files = [f for f in os.listdir(TEMPLATES_DIR) if f.endswith('.html') and f not in ['main_page.html', 'search_result.html']]

    # 각 HTML 파일을 열고 제목(h1)과 미리보기 내용을 검색어와 비교하여 일치하는 항목 찾기
    for file in html_files:
        file_path = os.path.join(TEMPLATES_DIR, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 파일에서 <h1> 태그로 감싸진 제목 추출
        title_start = content.find('<h1 class="title">')
        title_end = content.find('</h1>', title_start)
        title = content[title_start+len('<h1 class="title">'):title_end]

        # 파일에서 첫 번째 <p> 태그로 감싸진 미리보기 내용 추출
        preview_start = content.find('<p class="section-content">')
        preview_end = content.find('</p>', preview_start)
        preview = content[preview_start+len('<p class="section-content">'):preview_end]

        # 관련성 점수 계산 (제목과 미리보기에서 검색어가 나타나는 횟수를 더함)
        relevance_score = title.lower().count(query.lower()) + preview.lower().count(query.lower())

        # 관련 항목 리스트에 추가 (관련성 점수 포함)
        related_entries.append({
            'title': title,
            'preview': preview[:100] + '...',  # 미리보기 내용 일부만 표시
            'url': f'wiki/{file}',  # 파일의 URL 경로
            'relevance': relevance_score  # 관련성 점수 저장
        })

    # 관련성을 기준으로 정렬하되, 동일할 경우 제목을 알파벳 순으로 정렬
    sorted_entries = sorted(related_entries, key=lambda entry: (-entry['relevance'], entry['title'].lower()))

    # 최대 5개의 결과만 보여주도록 제한
    return render(request, 'wiki/search_result.html', {'query': query, 'related_entries': sorted_entries[:5]})