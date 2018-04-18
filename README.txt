Create a local web interface of a learning journal.
The main (index) page will list journal entry titles and dates.
Each journal entry title will link to a detail page
that displays the title, date, time spent, what you learned,
and resources to remember. Include the ability to add or edit
journal entries. When adding or editing a journal entry,
there must be prompts for title, date, time spent,
what you learned, resources to remember.
The results for these entries must be stored in a
database and displayed in a blog style website.
The HTML/CSS for this site has been supplied for you.

#######################################

After you’ve created a Flask project,
added all the required dependencies,
setup your project structure, and create a
Peewee model class for journal entries.
Add necessary routes for the application
/’ /entries /entries/<slug> /entries/edit/<slug>
/entries/delete/<slug> /entry

Create “list” view using the route /entries.
The list view contains a list of journal entries,
which displays Title and Date for Entry.
Title should be hyperlinked to the detail page
for each journal entry. Include a link to add an entry.

Create “details” view with the route “/details”
displaying the journal entry with all fields:
Title, Date, Time Spent, What You Learned, Resources to Remember.
Include a link to edit the entry.

Create “add/edit” view with the route “/entry”
that allows the user to add or edit journal entry
with the following fields: Title, Date, Time Spent,
What You Learned, Resources to Remember.

Add the ability to delete a journal entry.

Use the supplied HTML/CSS to build and style your pages.
Use CSS to style headings, font colors, journal
entry container colors, body colors.
Coding Style:
Make sure your coding style complies with PEP 8.

Before you submit your project for review,
make sure you can check off all of the items on the
Student Project Submission Checklist.
The checklist is designed to help you make
sure you’ve met the grading requirements and that
your project is complete and ready to be submitted!

##########################################

EXTRA:

Add tags to journal entries in the model.
Add tags to journal entries on the listing
page and allow the tags to be links to a list of specific tags.
Add tags to the details page.
Create password protection or user login
(provide credentials for code review).
Routing uses slugs.

NOTE:

To get an "Exceeds Expectations" grade for this project,
you'll need to complete each of the items in this section.
See the rubric in the "How You'll Be Graded" tab
above for details on how you'll be graded.
If you’re shooting for the "Exceeds Expectations"
grade, it is recommended that you mention so in your submission notes.
Passing grades are final. If you try
for the "Exceeds Expectations" grade, but miss an item
and receive a “Meets Expectations” grade, you won’t get
a second chance. Exceptions can be made for items
that have been misgraded in review.