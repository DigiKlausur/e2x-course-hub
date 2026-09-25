import { Routes, Route } from "react-router-dom";
import { CoursesPage } from "./components/courses/CoursesPage";
import { CoursePage } from "./components/course/CoursePage";
import { TermPage } from "./components/term/TermPage";

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-[#f5f7fb]">
      <Routes>
        {/* Unknown paths fall through to CoursesPage, which redirects them to
            its index. The /course routes still win because they are more
            specific. */}
        <Route path="/*" element={<CoursesPage />} />
        <Route path="/course/:courseId/*" element={<CoursePage />} />
        <Route path="/course/:courseId/term/:termId/*" element={<TermPage />} />
      </Routes>
    </div>
  );
}

export default App;
