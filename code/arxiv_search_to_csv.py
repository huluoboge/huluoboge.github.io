import arxiv
import csv
import argparse

def search_arxiv(keyword, max_results=50, output_file="arxiv_results.csv"):
    # 搜索
    print(f"🔍 正在检索关键词: {keyword}")
    search = arxiv.Search(
        query=keyword,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    # 写入 CSV
    with open(output_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Authors", "Published", "Summary", "arXiv ID", "URL"])

        for result in search.results():
            title = result.title.replace("\n", " ").strip()
            authors = ", ".join([a.name for a in result.authors])
            date = result.published.date() if result.published else ""
            summary = result.summary.replace("\n", " ").strip()
            arxiv_id = result.get_short_id()
            url = result.entry_id

            writer.writerow([title, authors, date, summary, arxiv_id, url])

    print(f"✅ 已保存 {max_results} 条结果到 {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search arXiv and export results to CSV.")
    parser.add_argument("--keyword", type=str, required=True, help="Search keyword, e.g. '3D Gaussian Splatting'")
    parser.add_argument("--max_results", type=int, default=50, help="Number of results to fetch")
    parser.add_argument("--output", type=str, default="arxiv_results.csv", help="Output CSV file name")
    args = parser.parse_args()

    search_arxiv(args.keyword, args.max_results, args.output)
