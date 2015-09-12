# because.moe
anime streaming search engine

Node.js, Python 3.4

# usage
This site serves a static JSON file containing a list of anime and their respective streaming sites.
To generate a new JSON file:
- Navigate to /generate/
- Run 'python generate.py'

The script should generate a new JSON file at /public/bcmoe.json
# deployment
- Run 'npm install' to install the relevant packages
- Navigate to the folder root
- Run 'node app.js'

The site should be available at http://localhost:3000

# license
The MIT License (MIT)

Copyright (c) 2015 Matthew Czubakowski (@mczub)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
