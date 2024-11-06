# Brain Snippets n-point

A Flask-based blog project integrated with [n:point](https://www.npoint.io/) for data storage.

## Live Demo

View a deployed version with this code at [blog.timonrieger.de](https://blog.timonrieger.de)

## Features

- Create, read, and view blog posts.
- Paginated list of blog posts.
- User-friendly text editor for creating and editing posts.
- Data stored and managed via n:point.
- Responsive design with Bootstrap.

## Requirements

- Python 3.x
- The following Python packages (as listed in `requirements.txt`):
  - Bootstrap_Flask==2.2.0
  - Flask_CKEditor==1.0.0
  - Flask_WTF==1.2.1
  - WTForms==3.0.1
  - Werkzeug==3.0.3
  - Flask==2.3.2
  - gunicorn==22.0.0
  - requests==2.31.0
  - pyperclip==1.8.2

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/timonrieger/brain-snippets-npoint.git
   ```

2. Navigate to the project directory:
   ```
   cd brain-snippets-npoint
   ```

3. Create a virtual environment:
   ```
   python -m venv venv
   ```

4. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

5. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

6. Set the required environment variables in a `.env` at the root directory. [Create a json bin first](https://www.npoint.io/):
   - `SECRET` (your flask secret key)
   - `n:pOINT` (the id of your npoint bin e.g. https://www.npoint.io/docs/55ec3c86cd78032d2742 > n:pOINT=55ec3c86cd78032d2742)

7. Run the application:
   ```
   python -m main
   ```

8. Write a post, submit the form and paste it in your json bin and rerun the application. Check the schema at [my n:point bin](https://www.npoint.io/docs/55ec3c86cd78032d2742) or view the [schema.json](schema.json)
To add images to your blog post upload the image to the `static/uploads/`directory and use it in the html code of your blog post text with `<img alt=\"\" src=\"https://blog.timonrieger.de/static/uploads/15.png\" style=\"height:100%; width:100%\" />`. Replace the URL with your deployed domain.

> **Warning**: Before submitting the form, copy the source HTML code to avoid data loss in case `pyperclip` fails.

## Endpoints

- **Home**: `/` - View all blog posts.
- **Post**: `/<post_title>` - View a single blog post.
- **New Post**: `/new-post` - Create a new blog post.
- **n:point**: `/npoint` - Redirect to n:point data page.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.