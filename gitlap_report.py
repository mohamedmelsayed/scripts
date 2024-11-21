import requests
import csv

# GitLab API configuration
GITLAB_URL = "https://gitlab.com"  # Replace with your GitLab instance URL
ACCESS_TOKEN = "your_access_token"  # Replace with your access token

# Fetch all projects
def get_all_projects():
    url = f"{GITLAB_URL}/api/v4/projects"
    headers = {"PRIVATE-TOKEN": ACCESS_TOKEN}
    params = {"membership": True, "per_page": 100}
    projects = []
    
    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        for project in data:
            projects.append({
                "id": project["id"],
                "name": project["name"],
                "last_activity_at": project["last_activity_at"]
            })
        url = response.links.get("next", {}).get("url")  # Get the next page URL if available
    
    return projects

# Fetch the last commit details for a project
def get_last_commit(project_id):
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/repository/commits"
    headers = {"PRIVATE-TOKEN": ACCESS_TOKEN}
    params = {"per_page": 1}  # Get only the latest commit
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    commits = response.json()
    if commits:
        return {
            "message": commits[0]["title"],
            "author_name": commits[0]["author_name"]
        }
    return {"message": None, "author_name": None}

# Save project data with commit details to CSV
def save_projects_to_csv(projects, output_file="gitlab_projects_with_commits.csv"):
    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["name", "last_activity_at", "last_commit_message", "last_commit_author"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        # Filter only required fields for CSV
        filtered_projects = [
            {
                "name": project["name"],
                "last_activity_at": project["last_activity_at"],
                "last_commit_message": project["last_commit_message"],
                "last_commit_author": project["last_commit_author"]
            }
            for project in projects
        ]
        writer.writerows(filtered_projects)
    print(f"Saved report as {output_file}")

# Main function to fetch and save project data with commits
if __name__ == "__main__":
    projects = get_all_projects()

    # Fetch last commit details for each project
    for project in projects:
        commit_details = get_last_commit(project["id"])
        project["last_commit_message"] = commit_details["message"]
        project["last_commit_author"] = commit_details["author_name"]

    # Save to CSV
    save_projects_to_csv(projects)

    # Print project names, last update dates, and last commit details
    for project in projects:
        print(f"Project: {project['name']}, Last Updated: {project['last_activity_at']}, "
              f"Last Commit: {project['last_commit_message']}, Author: {project['last_commit_author']}")
