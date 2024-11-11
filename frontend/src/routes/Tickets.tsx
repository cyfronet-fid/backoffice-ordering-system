import { useEffect, useState } from "react";
import { readTicketsTicketsGet, TicketPublic } from "../client";
import { Link } from "react-router-dom";

export function Tickets() {
  const [tickets, setTickets] = useState<TicketPublic[]>([]);
  const [ticketsLoaded, setTicketsLoaded] = useState(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error>();

  const loadTickets = async () => {
    setLoading(true);
    setError(undefined);

    // Simulate waiting for tickets a bit
    await new Promise((resolve) => setTimeout(resolve, 2000));

    try {
      const { data } = await readTicketsTicketsGet();
      setTickets(data ? data : []);
      setTicketsLoaded(true);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTickets();
  }, []);

  return (
    <>
      <Link to={"/"}>Back to root page</Link>

      <div className="generic-page">
        <div>
          <button onClick={loadTickets}>Load current tickets...</button>
        </div>

        {loading && <p>Loading tickets...</p>}
        {error && <p>Error loading tickets: {error.message}</p>}

        {ticketsLoaded && !loading && !error && (
          <div>
            <ul>
              {tickets.map((ticket, index) => (
                <li key={index}>{ticket.summary}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </>
  );
}
