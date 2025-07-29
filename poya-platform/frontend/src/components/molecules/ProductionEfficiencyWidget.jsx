import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import { Box, Paper, Typography } from '@mui/material';
import { format } from 'date-fns';

const ProductionEfficiencyWidget = ({ data }) => {
  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Production Efficiency (Last 30 Days)
      </Typography>
      <Box sx={{ width: '100%', height: 300 }}>
        <ResponsiveContainer>
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tickFormatter={(date) => format(new Date(date), 'MMM dd')}
            />
            <YAxis
              tickFormatter={(value) => `${value}%`}
              domain={[0, 100]}
            />
            <Tooltip
              labelFormatter={(date) => format(new Date(date), 'MMM dd, yyyy')}
              formatter={(value) => [`${value}%`, 'Efficiency']}
            />
            <Line
              type="monotone"
              dataKey="efficiency"
              stroke="#00C49F"
              activeDot={{ r: 8 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};

export default ProductionEfficiencyWidget;
