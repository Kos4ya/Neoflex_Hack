import Editor from '@monaco-editor/react';
import { useState } from 'react';
import './code-editor.css'

export const CodeEditor = () => {
    const [code, setCode] = useState("");
    return (
        <div className='code-editor'>
            <Editor
                defaultLanguage="typescript"
                defaultValue="// your code here"
                theme="vs-dark"
                onChange={(value) => setCode(value ?? '')}
                options={{
                    fontSize: 12,
                    fontFamily: "'JetBrains Mono', monospace",
                    minimap: { enabled: false },
                    scrollBeyondLastLine: false,
                    lineNumbersMinChars: 3,
                    automaticLayout: true
                }}
            />
        </div>
    )
}