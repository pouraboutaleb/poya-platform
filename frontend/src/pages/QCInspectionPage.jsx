import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { 
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Paper,
  Typography,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemText,
  Link
} from '@mui/material';
import { 
  fetchInspectionTasks, 
  getRouteCardDetails, 
  makeQCDecision,
  clearSelectedRouteCard 
} from '../store/qcInspectionSlice';

const QC_DECISIONS = {
  APPROVE: 'approve',
  REQUEST_REWORK: 'request_rework',
  REQUEST_SCRAP: 'request_scrap'
};

const QCInspectionPage = () => {
  const dispatch = useDispatch();
  const { tasks, selectedRouteCard, loading, error } = useSelector((state) => state.qcInspection);
  
  const [openDialog, setOpenDialog] = useState(false);
  const [notes, setNotes] = useState('');
  const [selectedTask, setSelectedTask] = useState(null);

  useEffect(() => {
    dispatch(fetchInspectionTasks());
  }, [dispatch]);

  const handleOpenDialog = async (task) => {
    setSelectedTask(task);
    await dispatch(getRouteCardDetails(task.route_card_id));
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setSelectedTask(null);
    setNotes('');
    setOpenDialog(false);
    dispatch(clearSelectedRouteCard());
  };

  const handleDecision = async (decision) => {
    await dispatch(makeQCDecision({
      taskId: selectedTask.id,
      decision,
      notes
    }));
    handleCloseDialog();
  };

  if (loading && tasks.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        QC Inspection Tasks
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error.message || 'An error occurred'}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Task ID</TableCell>
              <TableCell>Route Card</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Due Date</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tasks.map((task) => (
              <TableRow key={task.id}>
                <TableCell>{task.id}</TableCell>
                <TableCell>{task.route_card_id}</TableCell>
                <TableCell>{task.description}</TableCell>
                <TableCell>{new Date(task.due_date).toLocaleString()}</TableCell>
                <TableCell>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => handleOpenDialog(task)}
                  >
                    Inspect Part
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog 
        open={openDialog} 
        onClose={handleCloseDialog} 
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>QC Inspection Details</DialogTitle>
        <DialogContent>
          {selectedRouteCard && (
            <Box mt={2}>
              <Grid container spacing={3}>
                {/* Route Card Details */}
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Route Card Details
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="subtitle2">Route Card ID</Typography>
                          <Typography>{selectedRouteCard.route_card.id}</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="subtitle2">Status</Typography>
                          <Typography>{selectedRouteCard.route_card.status}</Typography>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Pickup Details */}
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Pickup Details
                      </Typography>
                      {selectedRouteCard.pickup_details.map((detail, index) => (
                        <Box key={index} mb={2}>
                          <Typography variant="subtitle2">
                            Picked up on: {new Date(detail.date).toLocaleString()}
                          </Typography>
                          <Typography>
                            Quantity: {detail.quantity_received}
                          </Typography>
                          <Link href={detail.invoice_url} target="_blank">
                            View Service Invoice
                          </Link>
                          {detail.notes && (
                            <Typography>Notes: {detail.notes}</Typography>
                          )}
                        </Box>
                      ))}
                    </CardContent>
                  </Card>
                </Grid>

                {/* Previous QC Logs */}
                {selectedRouteCard.qc_logs.length > 0 && (
                  <Grid item xs={12}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Previous QC Inspections
                        </Typography>
                        <List>
                          {selectedRouteCard.qc_logs.map((log, index) => (
                            <React.Fragment key={index}>
                              <ListItem>
                                <ListItemText
                                  primary={`Decision: ${log.decision}`}
                                  secondary={
                                    <>
                                      <Typography variant="body2">
                                        Date: {new Date(log.date).toLocaleString()}
                                      </Typography>
                                      {log.notes && (
                                        <Typography variant="body2">
                                          Notes: {log.notes}
                                        </Typography>
                                      )}
                                    </>
                                  }
                                />
                              </ListItem>
                              {index < selectedRouteCard.qc_logs.length - 1 && <Divider />}
                            </React.Fragment>
                          ))}
                        </List>
                      </CardContent>
                    </Card>
                  </Grid>
                )}

                {/* Notes Input */}
                <Grid item xs={12}>
                  <TextField
                    label="Inspection Notes"
                    multiline
                    rows={4}
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    fullWidth
                  />
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Box display="flex" gap={1}>
            <Button
              onClick={() => handleDecision(QC_DECISIONS.REQUEST_SCRAP)}
              color="error"
              variant="contained"
            >
              Request Scrap
            </Button>
            <Button
              onClick={() => handleDecision(QC_DECISIONS.REQUEST_REWORK)}
              color="warning"
              variant="contained"
            >
              Request Rework
            </Button>
            <Button
              onClick={() => handleDecision(QC_DECISIONS.APPROVE)}
              color="success"
              variant="contained"
            >
              Approve
            </Button>
          </Box>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default QCInspectionPage;
