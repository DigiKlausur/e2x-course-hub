import { Routes, Route } from "react-router-dom";
import CoursesPage from "./components/CoursesPage";
import CourseDetailPage from "./components/CourseDetailPage";
import ProfileDetailsPage from "./components/ProfileDetailsPage";

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-hbrs-dark-blue text-primary-foreground p-4 px-8 shadow-md">
        <h1 className="text-2xl font-semibold m-0 text-neutral-100">
          e²x Course Management
        </h1>
      </header>
      <main className="flex-1 p-8 bg-muted/30">
        <Routes>
          <Route path="/" element={<CoursesPage />} />
          <Route
            path="/course/:courseId/:termId"
            element={<CourseDetailPage />}
          />
          <Route
            path="/course/:courseId/:termId/profiles"
            element={<ProfileDetailsPage />}
          />
        </Routes>
      </main>
    </div>
  );
}

export default App;
