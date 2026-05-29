import Editor from "./tools/photo-generator/Editor";

// v1 is a single tool (photo generator). Future tools get their own folder under
// src/tools/ and a switcher here — the design intentionally has no app-level rail yet.
export default function App() {
  return <Editor />;
}
