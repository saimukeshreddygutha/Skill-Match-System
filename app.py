from flask import Flask, request
from resumeranker import jd_profile_comparison
from flask_cors import CORS
import requests
from docx import Document

from flask import * 


skills_url = "http://localhost:8080/jobseeker/username/%s"

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': 'http://localhost:3000'}})



obj_jd_profile_comparison = jd_profile_comparison()

def allowedExtension(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ['docx','pdf']

@app.route('/')
def hello():
    return "hello"


@app.route('/fileupload', methods = ['POST'])  
def fileupload():
        f = request.files["file"]
        document = Document(f)
        text = ''
        for paragraph in document.paragraphs:
            text += paragraph.text + '\n'

        f.save(f.filename)
        return {"resume_content": text}  
    

@app.route('/rank', methods=['POST'])
def getRank():
    data = request.get_json()
    job_desc = data.get("jobDesc")
    username = data.get("username")
    response = requests.get(skills_url % (username))
    jsdata = response.json()
    skills = jsdata["resumeContent"]
    return {"match": int(obj_jd_profile_comparison.match(job_desc, skills))}

@app.route('/sort_ads', methods=['POST'])
def getSortedAds():
    data  = request.get_json()
    jobads = data.get('jobAds')
    username = data.get("username")
    response = requests.get(skills_url % (username))
    data = response.json()
    skills = data["resumeContent"]

    print(skills)
    for jobad in jobads:
        jobad['match'] = obj_jd_profile_comparison.match(jobad['description'] + " " + jobad["skillsRequired"] + " "    + jobad["experienceRequired"], skills)
    

        
    
    jobads = sorted(jobads, key = lambda x: x['match'], reverse=True)

    return {"sortedJobAds": jobads}



if __name__ == '__main__':
    app.run(port=5000, debug=True)