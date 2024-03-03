# controllers/code_reviewer_service.py
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from github import Github, GithubIntegration
from bs4 import BeautifulSoup
import google.generativeai as genai
from google.generativeai import GenerativeModel
from flask import Blueprint, request, Response
import requests

class CodeReviewerService:
    @staticmethod
    def review_code(payload):
        owner = payload['repository']['owner']['login']
        repo_name = payload['repository']['name']
        pr_number = payload['number']
        diff_url = payload['pull_request']['diff_url']
        installation_id = payload['installation']['id']
        diff_text = CodeReviewerService.fetch_diff_text(diff_url)

        CodeReviewerService.review(owner, repo_name, pr_number, diff_text, installation_id)

    @staticmethod
    def fetch_diff_text(diff_url):
        r = requests.get(diff_url)
        diff_text = BeautifulSoup(r.content, 'html5lib').body.get_text()
        return diff_text

    @staticmethod
    def review(owner, repo_name, pr_number, diff_text, installation_id):
        # Initialize code review prompt and generative model
        prompt = '''
        You are an AI-powered code review tool that automatically scans code changes for bugs,
        security flaws, and coding best practices from diff. This tool provides instant feedback to
        developers, streamlining the review process and enhancing overall code quality. By
        leveraging this tool, the team ensures that only high-quality code is merged into the
        project, reducing the risk of bugs and vulnerabilities. Additionally, the tool learns from
        past reviews, continuously improving its analysis and further enhancing code quality
        over time.
        Check for:
        1) Unreachable code
        2) Waste variables like declaring but not using in its scope
        3) Exposing sensitives such as keys etc
        4) Syntax errors
        5) Check for wrong variable names comply to the programming language standards (For example, Java - camelcase, Python- snakecase)
        6) Code, design smells
        7) Additional generic linter errors (if any)
        8) Design pattern evaluation (if any)
        And any errors apart from it, each result must be specific with line number and file name

        Please give the summary of the code change in the diff.
        Code changes from diff:\n
        '''
        genai.configure(api_key=os.getenv("LLM_API_KEY"))
        model = GenerativeModel('gemini-pro')

        final_prompt = prompt + diff_text
        response = model.generate_content(final_prompt)

        # Initialize GitHub integration
        app_id = os.getenv("GHAPP_ID")
        private_key_path = os.getenv("PRIV_KEY_PATH")
        with open(private_key_path, 'r') as key_file:
            private_key = key_file.read()

        integration = GithubIntegration(app_id, private_key)
        access_token = integration.get_access_token(installation_id).token
        github = Github(access_token)
        repo = github.get_repo(f"{owner}/{repo_name}")
        pr = repo.get_pull(pr_number)

        # Create issue comment with code review suggestions
        pr.create_issue_comment("Here are a few suggestions:\n" + response.text)
