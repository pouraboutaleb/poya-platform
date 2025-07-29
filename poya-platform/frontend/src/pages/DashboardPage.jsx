import React, { useEffect, useState } from 'react';
import { Grid, Container, Paper, Typography, Box, CircularProgress } from '@mui/material';
import TaskOverviewWidget from '../components/molecules/TaskOverviewWidget';
import ProductionEfficiencyWidget from '../components/molecules/ProductionEfficiencyWidget';
import ActiveOrdersWidget from '../components/molecules/ActiveOrdersWidget';
import { dashboard } from '../api/apiClient';

const DashboardPage = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState({
    taskOverview: [],
    productionEfficiency: [],
    activeOrders: { procurement: 0, production: 0 }
  });

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const [taskOverview, productionEfficiency, activeOrders] = await Promise.all([
          dashboard.getTaskOverview(),
          dashboard.getProductionEfficiency(),
          dashboard.getActiveOrders()
        ]);

        setDashboardData({
          taskOverview: taskOverview.data,
          productionEfficiency: productionEfficiency.data,
          activeOrders: activeOrders.data
        });
      } catch (err) {
        setError('Failed to load dashboard data');
        console.error('Dashboard data fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();

    // Refresh dashboard data every 5 minutes
    const interval = setInterval(fetchDashboardData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="80vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg">
        <Paper
          sx={{
            p: 3,
            mt: 3,
            textAlign: 'center',
            color: 'error.main'
          }}
        >
          <Typography variant="h6">{error}</Typography>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Management Dashboard
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Task Overview Widget */}
        <Grid item xs={12} md={6}>
          <TaskOverviewWidget data={dashboardData.taskOverview} />
        </Grid>

        {/* Active Orders Widget */}
        <Grid item xs={12} md={6}>
          <ActiveOrdersWidget
            procurementOrders={dashboardData.activeOrders.procurement}
            productionOrders={dashboardData.activeOrders.production}
          />
        </Grid>

        {/* Production Efficiency Widget */}
        <Grid item xs={12}>
          <ProductionEfficiencyWidget data={dashboardData.productionEfficiency} />
        </Grid>
      </Grid>
    </Container>
  );
};

export default DashboardPage;
