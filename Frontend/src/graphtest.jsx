import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

function GraphTest() {
  const data = [
    { day: "Mon", power: 40 },
    { day: "Tue", power: 65 },
    { day: "Wed", power: 50 },
    { day: "Thu", power: 80 },
    { day: "Fri", power: 70 },
  ];

  return (
    <div>
      <h2>Solar Power Graph</h2>

      <LineChart width={600} height={300} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="day" />
        <YAxis />
        <Tooltip />

        <Line
          type="monotone"
          dataKey="power"
          stroke="#2563eb"
          strokeWidth={3}
        />
      </LineChart>
    </div>
  );
}

export default GraphTest;