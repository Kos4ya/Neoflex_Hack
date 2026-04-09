import Editor from '@monaco-editor/react';
import { useState } from 'react';
import './code-editor.css'

export const CodeEditor = () => {
    const [code, setCode] = useState("");
    return (
        <div className="ir-monaco-wrap">
            <Editor
              height="100%"
              defaultLanguage="typescript"
              defaultValue={CANDIDATE_CODE}
              theme="vs-dark"
              options={{
                readOnly: true,
                fontSize: 13,
                fontFamily: "'JetBrains Mono', monospace",
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                padding: { top: 16 },
                lineNumbersMinChars: 3,
                automaticLayout: true,
                domReadOnly: true,
                renderLineHighlight: 'none',
                cursorStyle: 'line-thin',
              }}/>
        </div>
    )
}