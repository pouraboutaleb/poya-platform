import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Container,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Alert,
  Chip
} from '@mui/material';
import {
  fetchOrders,
  selectOrdersLoading,
  selectOrdersError
} from '../../store/orderSlice';
import { api } from '../../api/apiClient';

const ProcurementPage = () => {
  const dispatch = useDispatch();
  const loading = useSelector(selectOrdersLoading);
  const error = useSelector(selectOrdersError);
  
  const [procurementOrders, setProcurementOrders] = useState([]);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [purchaseData, setPurchaseData] = useState({
    vendor_name: '',
    price: ''
  });
  const [dialogOpen, setDialogOpen] = useState(false);
  const [purchaseError, setPurchaseError] = useState(null);

  useEffect(() => {
    fetchProcurementOrders();
  }, []);

  const fetchProcurementOrders = async () => {
    try {
      const response = await api.get('/warehouse-requests/procurement');
      setProcurementOrders(response.data);
    } catch (error) {
      console.error('Error fetching procurement orders:', error);
    }
  };

  const handlePurchaseClick = (order) => {
    setSelectedOrder(order);
    setPurchaseData({
      vendor_name: order.vendor_name || '',
      price: order.price ? (order.price / 100).toString() : ''
    });
    setDialogOpen(true);
  };

  const handlePurchaseSubmit = async () => {
    try {
      setPurchaseError(null);
      await api.post(`/warehouse-requests/${selectedOrder.id}/mark-purchased`, purchaseData);
      setDialogOpen(false);
      fetchProcurementOrders(); // Refresh the list
    } catch (error) {
      setPurchaseError(error.response?.data?.detail || 'Error marking order as purchased');
    }
  };

  const formatCurrency = (amount) => {
    return amount ? `$${(amount / 100).toFixed(2)}` : '-';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Master Purchase List
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Order ID</TableCell>
              <TableCell>Item</TableCell>
              <TableCell>Quantity</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Required Date</TableCell>
              <TableCell>Vendor</TableCell>
              <TableCell>Price</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {procurementOrders.map((order) => (
              <TableRow key={order.id}>
                <TableCell>#{order.id}</TableCell>
                <TableCell>
                  {order.item ? order.item.name : `Item #${order.item_id}`}
                </TableCell>
                <TableCell>{order.quantity}</TableCell>
                <TableCell>
                  <Chip
                    label={order.priority}
                    color={order.priority === 'urgent' ? 'error' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {order.required_date
                    ? new Date(order.required_date).toLocaleDateString()
                    : 'Not set'}
                </TableCell>
                <TableCell>{order.vendor_name || '-'}</TableCell>
                <TableCell>{formatCurrency(order.price)}</TableCell>
                <TableCell>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => handlePurchaseClick(order)}
                  >
                    {order.vendor_name ? 'Update Purchase' : 'Mark Purchased'}
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>
          {selectedOrder?.vendor_name
            ? 'Update Purchase Details'
            : 'Mark Order as Purchased'}
        </DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          {purchaseError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {purchaseError}
            </Alert>
          )}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Vendor Name"
              fullWidth
              value={purchaseData.vendor_name}
              onChange={(e) =>
                setPurchaseData({ ...purchaseData, vendor_name: e.target.value })
              }
            />
            <TextField
              label="Price"
              type="number"
              fullWidth
              value={purchaseData.price}
              onChange={(e) =>
                setPurchaseData({ ...purchaseData, price: e.target.value })
              }
              InputProps={{
                startAdornment: '$'
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handlePurchaseSubmit} variant="contained" color="primary">
            Submit
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ProcurementPage;
