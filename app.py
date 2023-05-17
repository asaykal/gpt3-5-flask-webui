from flask import Flask, render_template, request, session, make_response, jsonify
import openai, csv, os, io, time, random, yaml

app = Flask(__name__)
app.secret_key = os.urandom(24)

api_key = os.environ.get("OPENAI_API_KEY")
openai.api_key = api_key

def retry_with_exponential_backoff(
    func,
    initial_delay: float = 15,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 10,
    errors: tuple = (openai.error.RateLimitError,),
):
    """Retry a function with exponential backoff."""
    def wrapper(*args, **kwargs):
        num_retries = 0
        delay = initial_delay

        while True:
            try:
                return func(*args, **kwargs)

            except errors as e:
                num_retries += 1

                if num_retries > max_retries:
                    raise Exception(
                        f"Maximum number of retries ({max_retries}) exceeded."
                    )

                delay *= exponential_base * (1 + jitter * random.random())

                time.sleep(delay)

            except Exception as e:
                raise e

    return wrapper

@retry_with_exponential_backoff
def completions_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)

@app.route('/')
def index():
    return render_template('index.html')

history = []

@app.route('/set_system_input', methods=['POST'])
def systeminput():
    system_input = request.form['system_input']
    session['system_input'] = system_input
    if history:
        for i in reversed(range(len(history))):
            history.pop(i)
    return system_input

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    system_input = session.get('system_input', '')
    if message:
        message_text = f"(Memory Log) Previous User message was : {message}"
        history.append((message_text, "\n"))  
        try:
            completion = completions_with_backoff(
                model="gpt-3.5-turbo",
                messages = [
                    {"role" : "system", "content" :   
                                                    """ 
                                                    You are an AI assistant capable of helping people with their daily tasks. The assistant is helpful, creative, clever, and very friendly. Your responses are in markdown format.
                                                    """ 
                                                    f"This is conversation history[ {history} ]"
                                                    "Avoid repeating yourself"
                                                    "Avoid saying the same thing twice"
                                                    },
                    {"role" : "system", "content" : f"{system_input}"},
                    {"role" : "user", "content" : f" {message} "}, 
                    {"role" : "assistant", "content" : "Assistant : "}
                    #{[msg for msg, _ in history]}
                            ],
                n=1,
                stop=None, 
                temperature=0.4,
            )
            response = completion['choices'][0]['message']['content']
            token_usage = completion['usage']['total_tokens']
            bot_response = response
            history[-1] = (history[-1][0], f"(Memory Log) Previous Assistant answer was : {bot_response}")  
            print(history)
            print("Token Usage : ", token_usage)
            if token_usage >= 3500:
                for i in reversed(range(len(history))):
                    history.pop(i)
            return bot_response
        except openai.error.APIError as error:
            return f"Error: {error.status_code}"
    else:
        return 'Error: Empty message'

@app.route('/export_history')
def export_history():
    output = io.StringIO()  
    writer = csv.writer(output)
    for msg, ans in history:
        if len(msg.strip()) > 0 and len(ans.strip()) > 0:
            writer.writerow([msg.strip()])
            writer.writerow([ans.strip()])
            writer.writerow([''])
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=history.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response 

@app.route('/upload_document', methods=['POST'])
def upload_document():
    history.clear() 
    document = request.files.get('document-file')
    if not document:
        return jsonify({'error': 'No file was uploaded.'}), 400
    document_contents = document.read().decode('utf-8')
    for line in document_contents.split('\n'):
        line = line.strip().rstrip('".')
        if len(line) > 0:
            history.append((line, ''))
    print(history)
    return jsonify({'document': document_contents}), 200

if __name__ == '__main__':
    app.run()
