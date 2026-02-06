#!/bin/bash

echo "=========================================="
echo "   Automated GitHub Deployment Helper"
echo "=========================================="
echo ""
echo "I cannot take your password (for your security!), but I can do everything else."
echo ""
echo "STEP 1: Go to https://github.com/new and create a repository."
echo "STEP 2: Copy the HTTPS URL (e.g., https://github.com/StartledFawn/my-repo.git)"
echo ""
read -p "Paste the Repository URL here: " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "Error: No URL provided. Please try again."
    exit 1
fi

echo ""
echo "Configuring remote..."
git remote remove origin 2>/dev/null
git remote add origin "$REPO_URL"
git branch -M main

echo ""
echo "Pushing code..."
echo "NOTE: A window may pop up asking you to log in. This is safe (it's GitHub)."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "SUCCESS! Code is on GitHub."
    echo "=========================================="
    echo "Final Step:"
    echo "1. Go to your repo settings on GitHub."
    echo "2. Go to 'Pages' section."
    echo "3. Set source to 'Deploy from a branch' -> 'main' -> '/docs' folder."
    echo "4. Save."
else
    echo ""
    echo "---------------------------------------------------------"
    echo "ERROR: The push failed."
    echo "If it said 'Authentication failed', it means you used your Password instead of a Token."
    echo ""
    echo "PLEASE READ: GITHUB_TOKEN_GUIDE.md"
    echo "It explains how to generate the 'ghp_...' token you need."
    echo "---------------------------------------------------------"
fi
