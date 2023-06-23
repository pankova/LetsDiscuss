# LetsDiscuss

#### Video Demo:  https://youtu.be/kmfX0q0yGck

#### Description:
**Let's Discuss** is an engaging and interactive couples questionnaire designed to enhance relationship communication and decision-making. 

This web-based platform provides thought-provoking questions and scenarios covering various aspects of life, such as decision-making, finances, shared interests, and more. By exploring these topics together, couples can deepen their understanding, strengthen their bond, and navigate important decisions as a team. 

Steps to Use:

1. User register via Google Auth
2. A partner link is generated
3. User send the link to their partner to answer questions together and compare their results later
4. User fill out the questionnaire for topics to discuss
5. Partner does the same
6. If both have answered, they can see their answers on the results page. Otherwise they will only see their own answers with question marks for their partner's answers
7. Once both have answered, they can discuss the suggested topics and their answers


## Tech details
```
Python, Flask, Jinja2, Javascript, Google Auth, HTML, CSS, SQLite
```
### Backend
- api.py _- backend part with navigation between pages and managing secure information like JWT-token_

### Frontend
- auth.js _- methods for Google authorization_
- partner_link.js _- common UI element with generated partner link for some pages_

**Pages**
- layout.html _- common UI for every page_
- index.html _- main page_

<img src="images/index.png" alt="Screenshot of an index page" width="400px">

- partner_link.html _- page describing partner link mechanic_

<img src="images/partner_link.png" alt="Screenshot of a partner link page" width="400px">

- questions.html _- question page_

<img src="images/questions.png" alt="Screenshot of a question page" width="400px">

- results.html _- user and user's partner answers_

<img src="images/results_without_partner.png" alt="Screenshot of a result page without partner answers" width="400px"><img src="images/results_with_partner.png" alt="Screenshot of a result page with partner answers" width="300px">

- styles.css

### Database
 SQLite database **questionnaire.db** with tables
- users (id, name, hash, partner_id)
- sections (id, text, page_order) _- question sections_
- questions (id, text, section_id)
- options (id, text) _- question options_
- results (user_id, question_id, option_id)

### Other
- helpers.py - utility methods
- models.py - application entities like User, Question, Optin, etc 
