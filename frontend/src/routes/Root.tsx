import { Link } from "react-router-dom";

export default function Root() {
  return (
    <div className="generic-page">
      <h1>Welcome to Backoffice Ordering System!</h1>
      <Link to={"tickets"}>Go to tickets</Link>
    </div>
  );
}
