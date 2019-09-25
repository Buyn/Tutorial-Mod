#! /bin/sh
echo "start ading aliases. use '. ./' for permnent"
git config --global user.name "BuYn"
git config --global user.email "buyn.tex@gmail.com"
alias st="git status"
alias gh="git push"
alias gad="git add ."
alias gig="echo >>.gitignore"
alias ac="git commit *"
alias gmme="git checkout master; git merge experemental; git checkout experemental"
alias gmem="git checkout experemental; git merge master; git checkout master"
alias gmte="git checkout test; git merge experemental; git checkout experemental"
alias gmmt="git checkout master; git merge test; git checkout experemental"

